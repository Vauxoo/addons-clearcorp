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