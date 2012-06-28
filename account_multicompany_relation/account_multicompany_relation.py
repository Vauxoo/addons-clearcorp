# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Mag Guevara. Copyright ClearCorp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from copy import copy

class account_multicompany_relation(osv.osv):
    _name = "account.multicompany.relation"
    _columns = {
        'name'              :    fields.char('Name',size=64, required=True,help='Name for the mirror object relation'),
        'origin_account'    :    fields.many2one('account.account', 'Original Account',help='Indicate the original account where the transaction is taking place'),
        'targ_account'      :    fields.many2one('account.account', 'Target Account',help='Indicate the target account where the transaction of the original account has to be seen, this is an account from another company'),
        'origin_journal'    :    fields.many2one('account.journal', 'Original Journal',help='Indicate the original journal where the transaction is taking place'),
        'targ_journal'      :    fields.many2one('account.journal', 'Target Journal',help='Indicate the original account where the transaction is taking place'),
    }

    _sql_constraints = [
        (
            'unique_name', 
            'unique(name)',
            'The name must be unique'
        ),
        (   
            'unique_journal_account_origins', 
            'unique(origin_account,origin_journal)', 
            'Already exist a relation to this diary and account (origins)'
        )
    ]

account_multicompany_relation()

class account_voucher_journal_payment(osv.osv):
    _name = 'account.voucher'
    _inherit = 'account.voucher'
    _description = 'Accounting Voucher'

    def proforma_voucher(self, cr, uid, ids, context=None):
        result = super(account_voucher_journal_payment, self).action_move_line_create(cr, uid, ids, context=context)
        voucher = self.browse(cr,1,ids,context=context)[0]
        cuenta = voucher.account_id.id
        diario = voucher.journal_id.id
        mirror_journal_id = self.pool.get('account.multicompany.relation').search(cr, 1, [('origin_account', '=', cuenta), ('origin_journal', '=', diario)], context=context)[0]
        if mirror_journal_id:
            mirror_journal = self.pool.get('account.multicompany.relation').browse(cr, 1, [mirror_journal_id], context=context)[0]
            origin_journal = mirror_journal.origin_journal
            origin_account = mirror_journal.origin_account
            targ_journal =  mirror_journal.targ_journal
            targ_account = mirror_journal.targ_account

            if voucher.move_id:
                original_move = voucher.move_id
                
                if original_move.line_id:
                    list_ = []
                    lines = original_move.line_id
                    for line in lines:
                        if line.account_id and line.account_id.id == origin_account.id:
                            list_.append(line)
                
                    if len(list_) == 1:
                        #Set period for target move with the correct company
                        if context == None:
                            context_copy = {'company_id': targ_account.company_id.id}
                        else:
                            context_copy = copy(context)
                            context_copy.update({'company_id': targ_account.company_id.id})
                        periods = self.pool.get('account.period').find(cr, 1, dt=original_move.date, context=context_copy)
                        if periods:
                            move_period = periods[0]

                        move = {
                            'name':'auto: ' + original_move.name,
                            'ref':original_move.ref,
                            'journal_id':targ_journal.id,
                            'period_id':move_period or False,
                            'to_check':False,
                            'partner_id':original_move.partner_id.id,
                            'date':original_move.date,
                            'narration':original_move.narration,
                            'company_id':targ_account.company_id.id,
                        }
                        move_id = self.pool.get('account.move').create(cr, 1, move)
            
                        move_line_original = list_[0]

                        move_line_one = {
                            'name':move_line_original.name,
                            'debit':move_line_original.credit,
                            'credit':move_line_original.debit,
                            'account_id':targ_account.id,
                            'move_id': move_id,
                            'amount_currency':move_line_original.amount_currency * -1,
                            'period_id':move_period or False,
                            'journal_id':targ_journal.id,
                            'partner_id':move_line_original.partner_id.id,
                            'currency_id':move_line_original.currency_id.id,                   
                            'date_maturity':move_line_original.date_maturity,
                            'date':move_line_original.date,
                            'date_created':move_line_original.date_created,
                            'state':'valid',
                            'company_id':targ_account.company_id.id,
                        }

                        self.pool.get('account.move.line').create(cr, 1, move_line_one)
                        if move_line_original.debit != 0.0:
                            move_line_two_account_id = targ_journal.default_credit_account_id
                        else:
                            move_line_two_account_id = targ_journal.default_debit_account_id

                        move_line_two = {
                            'name':move_line_original.name,
                            'debit':move_line_original.debit,
                            'credit':move_line_original.credit,
                            'account_id':move_line_two_account_id.id,
                            'move_id': move_id,
                            'amount_currency':move_line_original.amount_currency,
                            'journal_id':targ_journal.id,
                            'period_id':move_period or False,
                            'partner_id':move_line_original.partner_id.id,
                            'currency_id':move_line_original.currency_id.id,                   
                            'date_maturity':move_line_original.date_maturity,
                            'date':move_line_original.date,
                            'date_created':move_line_original.date_created,
                            'state':'valid',
                            'company_id':targ_account.company_id.id,
                        }

                        self.pool.get('account.move.line').create(cr, 1, move_line_two)
                        
                        if (targ_journal.entry_posted):
                            self.pool.get('account.move').post(cr, 1, [move_id], context={})
        return result

account_voucher_journal_payment()
