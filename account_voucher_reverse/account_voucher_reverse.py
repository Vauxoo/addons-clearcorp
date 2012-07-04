# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
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

class account_voucher_reverse(osv.osv):
    _name = 'account.voucher'
    _inherit = 'account.voucher'

    _columns = {
        'state':fields.selection(
            [('draft','Draft'),
             ('proforma','Pro-forma'),
             ('posted','Posted'),
             ('reverse','Reverse'),
             ('cancel','Cancelled')
            ], 'State', readonly=True, size=32,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma state,voucher does not have an voucher number. \
                        \n* The \'Posted\' state is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Reverse\' state is used when user reverse voucher \
                        \n* The \'Cancelled\' state is used when user cancel voucher.'),
    }

    def reverse_voucher(self, cr, uid, ids, context=None):

        self.write(cr, uid, ids, {'state' : 'reverse'}, context=context)

        #To create a move reverse
        self.account_voucher_move_reverse(cr, uid, ids, context=context)
        
        return True

    def account_voucher_move_reverse(self, cr, uid, ids, context=None):
        # Initialize voucher variables and check if voucher has a move, a journal and an account
        # If not, exit and return original result
        voucher = self.browse(cr,uid,ids,context=context)[0]
        if not voucher.move_id:
            return False

        original_move = voucher.move_id
        
        if not original_move.line_id:
            return False

        move = {
            'name':'Reverse: ' + original_move.name,
            'ref':original_move.ref,
            'journal_id':original_move.journal_id.id,
            'period_id':original_move.period_id.id,
            'to_check':False,
            'partner_id':original_move.partner_id.id,
            'date':original_move.date,
            'narration':original_move.narration,
            'company_id':original_move.company_id.id,
        }
        move_id = self.pool.get('account.move').create(cr, uid, move)

        move_reconcile_obj = self.pool.get('account.move.reconcile')

        lines = original_move.line_id
        for line in lines:
            move_line = {
                'name':line.name,
                'debit':line.credit,
                'credit':line.debit,
                'account_id':line.account_id.id,
                'move_id': move_id,
                'amount_currency':line.amount_currency * -1,
                'period_id':line.period_id.id,
                'journal_id':line.journal_id.id,
                'partner_id':line.partner_id.id,
                'currency_id':line.currency_id.id,
                'date_maturity':line.date_maturity,
                'date':line.date,
                'date_created':line.date_created,
                'state':'valid',
                'company_id':line.company_id.id,
            }

            line_created_id = self.pool.get('account.move.line').create(cr, uid, move_line)
            
            if (original_move.journal_id.entry_posted):
                self.pool.get('account.move').post(cr, uid, [move_id], context={})

            if line.reconcile_id:
                reconcile = move_reconcile_obj.browse(cr,uid,[line.reconcile_id.id],context=context)[0]
                if len(reconcile.line_id) > 2:
                    self.pool.get('account.move.line').write(cr,uid,line.id,{'reconcile_id': False })
                    for line in reconcile.line_id:
                        self.pool.get('account.move.line').write(cr,uid,line.id,{'reconcile_id': False,'reconcile_partial_id':line.reconcile_id.id})
                else:
                    move_reconcile_obj.unlink(cr,uid,[line.reconcile_id.id],context=context)
            
            if line.reconcile_partial_id:
                reconcile = move_reconcile_obj.browse(cr,uid,[line.reconcile_partial_id.id],context=context)[0]
                if len(reconcile.line_partial_ids) > 2:
                    self.pool.get('account.move.line').write(cr,uid,line.id,{'reconcile_partial_id': False })
                else:
                    move_reconcile_obj.unlink(cr,uid,[line.reconcile_partial_id.id],context=context)

            if line.account_id.reconcile:
                reconcile_id = self.pool.get('account.move.reconcile').create(cr, uid, {'type': 'Account Reverse'})
                self.pool.get('account.move.line').write(cr,uid,[line.id],{'reconcile_id': reconcile_id})
                self.pool.get('account.move.line').write(cr,uid,[line_created_id],{'reconcile_id': reconcile_id})

        return True















