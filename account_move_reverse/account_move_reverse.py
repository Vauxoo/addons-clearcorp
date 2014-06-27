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

from osv import orm, osv, fields
from tools.translate import _

class AccountMove(orm.Model):

    _inherit = 'account.move'

    #Add a reversed and reversion state to account.move.
    #Reversed state is for moves that have been reverted.
    #Reversion state is for moves that are created based on another move. It's the move reverse.
    _columns = {
        'move_reverse_id':fields.many2one('account.move','Move Reverse'),
        'state': fields.selection(
                    [('draft','Unposted'), 
                     ('posted','Posted'),
                     ('reversed','Reversed'),
                     ('reversion','Reversion')], 
                    'Status', required=True, readonly=True, 
                   help='All manually created new journal entries are usually in the status \'Unposted\', but you can set the option to skip that status on the related journal. \
                        \n* In that case, they will behave as journal entries automatically created by the system on document validation (invoices, bank statements...) and will be created in \'Posted\' status. \
                        \n* The \'Reversed\' state is used the move have a move reversed \
                        \n* The \'Reversion\' state is used when the move is a move reverse that is created when the move is reverse.'),
    }

    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'move_reverse_id':False,
        })
        return super(AccountMove, self).copy(cr, uid, id, default, context)

    def button_cancel(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if not move.journal_id.update_posted:
                raise osv.except_osv(_('Error !'), _('You can not modify a posted entry of this journal !\nYou should set the journal to allow cancelling entries if you want to do that.'))

            if move.move_reverse_id:
                if not move.journal_id.update_reversed:
                    raise osv.except_osv(_('Error !'), _('You can not modify a posted entry of this journal !\nYou should set the journal to allow cancelling reversed entries if you want to do that.'))
                
                move_reverse = self.browse(cr, uid, move.move_reverse_id.id, context=context)
                for line_reverse in move_reverse.line_id:
                    if line_reverse.reconcile_id:
                        self.pool.get('account.move.reconcile').unlink(cr,uid,[line_reverse.reconcile_id.id],context=context)
                cr.execute('UPDATE account_move '\
                           'SET state=%s '\
                           'WHERE id IN %s', ('draft', tuple([move_reverse.id]),))
                self.unlink(cr,uid,[move_reverse.id],context=context)

        result = super(AccountMove, self).button_cancel(cr, uid, ids, context=context)
        return True

    def reverse(self, cr, uid, ids, context=None):

        for move_original_id in ids:
            new_reconcile_line_ids = []
            move_original = self.pool.get('account.move').browse(cr, 1, move_original_id, context=context)
            
            if move_original.move_reverse_id:
                continue
            
            if move_original.state == 'draft':
                #Posted move original
                self.pool.get('account.move').post(cr, 1, [move_original.id], context={})
            
            move = {
                    'name':'Reverse: ' + move_original.name,
                    'ref':move_original.ref,
                    'journal_id':move_original.journal_id.id,
                    'period_id':move_original.period_id.id,
                    'to_check':False,
                    'partner_id':move_original.partner_id.id,
                    'date':move_original.date,
                    'narration':move_original.narration,
                    'company_id':move_original.company_id.id,
                    }
            move_id = self.pool.get('account.move').create(cr, uid, move)
                    
            self.pool.get('account.move').write(cr, uid, [move_original.id], {'move_reverse_id' : move_id})

            move_reconcile_obj = self.pool.get('account.move.reconcile')

            lines = move_original.line_id
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

                if line.reconcile_id:
                    reconcile = line.reconcile_id
                    if len(reconcile.line_id) > 2:
                        reconcile_line_ids = []
                        for line_id in reconcile.line_id:
                            if line_id.id not in new_reconcile_line_ids:
                                reconcile_line_ids.append(line_id.id)
                        if len(reconcile_line_ids) > 2:
                            self.pool.get('account.move.line').write(cr,uid,reconcile_line_ids,{'reconcile_id': False, 'reconcile_partial_id':reconcile.id})
                            self.pool.get('account.move.line').write(cr,uid,line.id,{'reconcile_partial_id': False})
                        else:
                            move_reconcile_obj.unlink(cr,uid,[reconcile.id],context=context)
                        new_reconcile_line_ids.append(line.id) #Workaround, commit database
                        
                    else:
                        move_reconcile_obj.unlink(cr,uid,[reconcile.id],context=context)

                elif line.reconcile_partial_id:
                    reconcile = line.reconcile_partial_id
                    if len(reconcile.line_partial_ids) > 2:
                        self.pool.get('account.move.line').write(cr,uid,line.id,{'reconcile_partial_id': False })
                    else:
                        move_reconcile_obj.unlink(cr,uid,[reconcile.id],context=context)

                if line.account_id.reconcile:
                    reconcile_id = self.pool.get('account.move.reconcile').create(cr, uid, {'type': 'Account Reverse'})
                    
                    #The move don't support write this line
                    cr.execute('UPDATE account_move_line '\
                               'SET reconcile_id=%s '\
                               'WHERE id IN %s', (reconcile_id, tuple([line.id]),))
                    #self.pool.get('account.move.line').write(cr,uid,[line.id],{'reconcile_id': reconcile_id})
                    self.pool.get('account.move.line').write(cr,uid,[line_created_id],{'reconcile_id': reconcile_id})

            #Posted move reverse
            self.pool.get('account.move').post(cr, 1, [move_id, move_original.id], context={})
            
            #Change in move state 8/7/2013 -> Diana Rodriguez
            '''
                A move that is reversed can't reverse again. A move that is create from a move is a reversion
                and also can't reverse again. Write the states of move_id (reversion) and move_original (reversed).
            '''
            self.write(cr, uid, [move_id], {'state' : 'reversion'}, context=context) 
            self.write(cr, uid, [move_original.id], {'state' : 'reversed'}, context=context)
            
        return True
    
    #Action that is call in button.
    def reverse_move_button(self, cr, uid, ids, context):
        return self.reverse(cr, uid, ids,context=context)


class AccountJournal(orm.Model):
    _inherit = 'account.journal'
    
    _columns = {
        'update_reversed' : fields.boolean('Allow Cancelling Reversed Entries', help="Check this box if you want to allow the cancellation of the reversed entries related to this journal or of the invoice related to this journal"),
        }
