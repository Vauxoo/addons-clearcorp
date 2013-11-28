# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

##############################################################################
#    Collaboration by:
#    CLEARCORP S.A.- Copyright (C) 2009-TODAY 
#    (<http://clearcorp.co.cr>).
###############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
    
class accountBankStatement(osv.Model):
    '''
    Extensions from account_bank_statement:
        1. Removed period_id (transformed to optional boolean) - as it is no
           longer needed.
           NB! because of #1. changes required to account_voucher!
        2. Extended 'button_confirm' trigger to cope with the period per
           statement_line situation.
        3. Added optional relation with imported statements file
        4. Ordering is based on auto generated id.
    '''
    _inherit = 'account.bank.statement'
    _order = 'id'
    
    def _check_company_id(self, cr, uid, ids, context=None):
        """
        Adapt this constraint method from the account module to reflect the
        move of period_id to the statement line
        """
        for statement in self.browse(cr, uid, ids, context=context):
            if (statement.period_id and
                statement.company_id.id != statement.period_id.company_id.id):
                return False
        return True
    

    """def _get_period(self, cursor, uid, date, context=None):
        '''
        Find matching period for date, not meant for _defaults.
        '''
        period_obj = self.pool.get('account.period')
        periods = period_obj.find(cursor, uid, dt=date, context=context)
        return periods and periods[0] or False"""

    def _end_balance(self, cursor, user, ids, name, attr, context=None):
        """
        This method taken from account/account_bank_statement.py and
        altered to take the statement line subflow into account
        """
        res = {}
    
        statements = self.browse(cursor, user, ids, context=context)
        for statement in statements:
            res[statement.id] = statement.balance_start

            # Calculate the balance based on the statement line amounts
            # ..they are in the statement currency, no conversion needed.
            for line in statement.line_ids:
                res[statement.id] += line.amount
     
        for r in res:
            res[r] = round(res[r], 2)
        return res

    '''def button_confirm_bank(self, cr, uid, ids, context=None):
        """ Inject the statement line workflow here """
        if context is None:
            context = {}
        line_obj = self.pool.get('account.bank.statement.line')
        for st in self.browse(cr, uid, ids, context=context):
            j_type = st.journal_id.type
            if not self.check_status_condition(cr, uid, st.state, journal_type=j_type):
                continue

            self.balance_check(cr, uid, st.id, journal_type=j_type, context=context)
            if (not st.journal_id.default_credit_account_id) \
                    or (not st.journal_id.default_debit_account_id):
                raise osv.except_osv(_('Configuration Error !'),
                        _('Please verify that an account is defined in the journal.'))

            # protect against misguided manual changes
            for line in st.move_line_ids:
                if line.state != 'valid':
                    raise osv.except_osv(_('Error !'),
                            _('The account entries lines are not in valid state.'))

            line_obj.confirm(cr, uid, [line.id for line in st.line_ids], context)
            st.refresh()
            self.log(cr, uid, st.id, _('Statement %s is confirmed, journal '
                                       'items are created.') % (st.name,))
        return self.write(cr, uid, ids, {'state':'confirm'}, context=context)'''
    
    def button_confirm_bank(self, cr, uid, ids, context=None):
        result = super(accountBankStatement,self).button_confirm_bank(cr, uid, ids, context)
        #self.reconcile(cr, uid, ids, context)
        return result
    
    def _reconcile_null_balance(self, cr, uid, ids, account_id, context=None):
        move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}
        reconciled = 0
        params = (account_id.id,)
        query = """SELECT partner_id FROM account_move_line WHERE account_id=%s AND reconcile_id IS NULL
        AND state <> 'draft' GROUP BY partner_id
        HAVING ABS(SUM(debit-credit)) = 0.0 AND count(*)>0"""
        # Reconcile automatically all transactions from partners whose balance is 0
        cr.execute(query, params)
        partner_ids = [id for (id,) in cr.fetchall()]
        for partner_id in partner_ids:
            cr.execute(
                "SELECT id " \
                "FROM account_move_line " \
                "WHERE account_id=%s " \
                "AND partner_id=%s " \
                "AND state <> 'draft' " \
                "AND reconcile_id IS NULL",
                (account_id.id, partner_id))
            line_ids = [id for (id,) in cr.fetchall()]
            if line_ids:
                reconciled += len(line_ids)
                #if allow_write_off: ELIMINAR
                    #move_line_obj.reconcile(cr, uid, line_ids, 'auto', form.writeoff_acc_id.id, form.period_id.id, form.journal_id.id, context)
                #else:
                move_line_obj.reconcile_partial(cr, uid, line_ids, 'manual', context=context)
        return reconciled
    
    def _reconcile(self, cr, uid, ids, account_id, context=None):
        automatic_reconcile_obj = self.pool.get('account.automatic.reconcile')
        if context is None:
            context = {}
        # Define default parameters to be used with the automatic
        # reconcile max_amount = 0.0 not allowing mismatch between
        # move_lines, power = 2 allowing only to match 2 move_lines
        # and allow_write_off set to False
        max_amount = 0.0
        power = 2
        # Get the list of partners who have more than one unreconciled transaction
        cr.execute(
            "SELECT partner_id " \
            "FROM account_move_line " \
            "WHERE account_id=%s " \
            "AND reconcile_id IS NULL " 
            "AND state <> 'draft' " \
            "AND partner_id IS NOT NULL " \
            "GROUP BY partner_id " \
            "HAVING count(*)>1",
            (account_id.id,))
        partner_ids = [id for (id,) in cr.fetchall()]
        # Filter?
        for partner_id in partner_ids:
            # Get the list of unreconciled 'debit transactions' for this partner
            cr.execute(
                "SELECT id, debit " \
                "FROM account_move_line " \
                "WHERE account_id=%s " \
                "AND partner_id=%s " \
                "AND reconcile_id IS NULL " \
                "AND state <> 'draft' " \
                "AND debit > 0 " \
                "ORDER BY date_maturity",
                (account_id.id, partner_id))
            debits = cr.fetchall()

            # get the list of unreconciled 'credit transactions' for this partner
            cr.execute(
                "SELECT id, credit " \
                "FROM account_move_line " \
                "WHERE account_id=%s " \
                "AND partner_id=%s " \
                "AND reconcile_id IS NULL " \
                "AND state <> 'draft' " \
                "AND credit > 0 " \
                "ORDER BY date_maturity",
                (account_id.id, partner_id))
            credits = cr.fetchall()
            automatic_reconcile_obj.do_reconcile(
                cr, uid, credits, debits, max_amount,
                power, False, False, False, context)
        return partner_ids
        
    def reconcile(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        result = []
        reconciled = 0
        unreconciled = 0
        statements = self.browse(cr, uid, ids, context)
        for statement in statements:
            account_ids = None
            try:
                account_ids = [
                               statement.banking_id.bank_id.default_credit_account_id,
                               statement.banking_id.bank_id.default_debit_account_id,
                               ]# REVISAR
            except:
                raise osv.except_osv(
                                     _('Error'),
                                     _('Couldn\'t locate default debit'
                                       ' account or default credit account')
                                     )
            for account_id in account_ids:
                reconciled += self._reconcile_null_balance(cr, uid, ids, account_id, context)
                partner_ids = self._reconcile(cr, uid, ids, account_id, context)
                #reconciled += res[0]
                #unreconciled += res[1]
                
                # Add the number of transactions for partners who have only one
                # Unreconciled transactions to the unreconciled count
                partner_filter = partner_ids and 'AND partner_id not in (%s)' % ','.join(map(str, filter(None, partner_ids))) or ''
                cr.execute(
                    "SELECT count(*) " \
                    "FROM account_move_line " \
                    "WHERE account_id=%s " \
                    "AND reconcile_id IS NULL " \
                    "AND state <> 'draft' " + partner_filter,
                    (account_id.id,))
                additional_unrec = cr.fetchone()[0]
                unreconciled = unreconciled + additional_unrec
            result.append((statement.id, reconciled, unreconciled))
        return result
        #context.update({'reconciled': reconciled, 'unreconciled': unreconciled})
        #model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','account_automatic_reconcile_view1')])
        #resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']

            

    _constraints = [
                    (_check_company_id, 'The journal and period chosen have to belong'
                     ' to the same company.', ['journal_id','period_id']),
                    ]

    _columns = {
                # override this field *only* to replace the 
                # function method with the one from this module.
                # Note that it is defined twice, both in
                # account/account_bank_statement.py (without 'store') and
                # account/account_cash_statement.py (with store=True)
                'balance_end': fields.function(_end_balance, method=True,
                                               store=True, string='Balance'),
                'banking_id': fields.many2one('account.banking.ccorp.imported.file',
                                              'Imported File', readonly=True),
                }