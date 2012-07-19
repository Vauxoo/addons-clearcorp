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

from osv import orm, osv, fields
from copy import copy
from tools.translate import _

class account_multicompany_relation(orm.Model):

    _name = "account.multicompany.relation"
    _description = "Account multicompany relation"

    _columns = {
        'name':fields.char('Name',size=64,required=True,help='Name for the mirror object relation'),
        'origin_account':fields.many2one('account.account','Original Account',required=True,help='Indicate the original account where the transaction is taking place'),
        'targ_account':fields.many2one('account.account','Target Account',required=True,help='Indicate the target account where the transaction of the original account has to be seen, this is an account from another company'),
        'origin_journal':fields.many2one('account.journal','Original Journal',required=True,help='Indicate the original journal where the transaction is taking place'),
        'targ_journal':fields.many2one('account.journal','Target Journal',required=True,help='Indicate the original account where the transaction is taking place'),
        'origin_analytic_account':fields.many2one('account.analytic.account','Original Analytic Account',required=False,help='Indicate the original analytic account where the transaction is taking place'),
        'targ_analytic_account':fields.many2one('account.analytic.account','Target Analytic Account',required=False,help='Indicate the target analytic account where the transaction of the original analytic account has to be seen, this is an analytic account from another company'),
    }

    _sql_constraints = [
        (
            'unique_name',
            'unique(name)',
            'The name must be unique'
        ),
        (
            'unique_mirror_relation',
            'unique(origin_account,origin_journal,origin_analytic_account)',
            'A relation exists already'
        )
    ]

    def _check_unique_mirror_relation(self, cr, uid, ids, context=None):
        exist = False
        all_mirrors_ids = self.search(cr, uid, [], context)
        all_mirrors = self.browse(cr, uid, all_mirrors_ids, context)
        for mirror_id in ids:
            mirror = self.browse(cr, uid, mirror_id, context)
            if not mirror.origin_analytic_account:
                for current_mirror in all_mirrors:
                    if current_mirror.origin_account.id == mirror.origin_account.id and current_mirror.origin_journal.id == mirror.origin_journal.id:
                        if not current_mirror.origin_analytic_account:
                            return False
        return True

    _constraints = [
        (
            _check_unique_mirror_relation,
            'A relation exists already', ['origin_analytic_account']
        )
    ]

class AccountMoveLine(orm.Model):

    _inherit = 'account.move.line'
    
    _columns = {
                'move_mirror_rel_id':fields.many2one('account.move','Move Multicompany Relation'),
                }
    
    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'move_mirror_rel_id':False,
        })

class account_move(orm.Model):

    _inherit = 'account.move'

    def button_cancel(self, cr, uid, ids, context=None):
        self.pool.get('account.move.reconcile')
        for move in self.browse(cr, uid, ids, context=context):
            if not move.journal_id.update_posted:
                raise osv.except_osv(_('Error !'), _('You can not modify a posted entry of this journal !\nYou should set the journal to allow cancelling entries if you want to do that.'))

            #Set user administrator to run this portion of code
            uid = 1
            for line in move.line_id:
                if line.move_mirror_rel_id:
                    move_mirror = self.browse(cr, uid, line.move_mirror_rel_id.id, context=context)
                    if not move_mirror.journal_id.update_posted:
                        raise osv.except_osv(_('Error !'), _('You can not modify a posted multicompany mirror entry of this journal !\nYou should set the journal to allow cancelling entries if you want to do that.'))

            move_reconcile_obj = self.pool.get('account.move.reconcile')

            for line in move.line_id:
                if line.move_mirror_rel_id:
                    move_mirror = self.browse(cr, uid, line.move_mirror_rel_id.id, context=context)

                    for line_mirror in move_mirror.line_id:
                        if line_mirror.reconcile_id:
                            reconcile = line_mirror.reconcile_id
                            if len(reconcile.line_id) > 2:
                                self.pool.get('account.move.line').write(cr,uid,reconcile.line_id,{'reconcile_id': False, 'reconcile_partial_id':reconcile.id})
                                self.pool.get('account.move.line').write(cr,uid,line_mirror.id,{'reconcile_partial_id': False})
                            else:
                                move_reconcile_obj.unlink(cr,uid,[reconcile.id],context=context)

                        elif line_mirror.reconcile_partial_id:
                            reconcile = line_mirror.reconcile_partial_id
                            if len(reconcile.line_partial_ids) > 2:
                                self.pool.get('account.move.line').write(cr,uid,line_mirror.id,{'reconcile_partial_id': False })
                            else:
                                move_reconcile_obj.unlink(cr,uid,[reconcile.id],context=context)

                    cr.execute('UPDATE account_move '\
                               'SET state=%s '\
                               'WHERE id IN %s', ('draft', tuple([move_mirror.id]),))
                    self.button_cancel(cr,uid,[move_mirror.id],context=context)
                    self.unlink(cr,uid,[move_mirror.id],context=context)

        result = super(account_move, self).button_cancel(cr, uid, ids, context=context)
        return True

    def post(self, cr, uid, ids, context=None):
        result = super(account_move, self).post(cr, uid, ids, context=context)

        for move_id_original in ids:
            if self.pool.get('account.move').search(cr, 1, [('move_reverse_id', '=', move_id_original)], context=context):
                continue
                            
            original_move = self.pool.get('account.move').browse(cr, 1, move_id_original, context=context)
            
            if original_move.line_id:
                mirror_selected = False

                for line in original_move.line_id:
                    if line.move_mirror_rel_id:
                        if original_move.move_reverse_id:
                            self.pool.get('account.move').reverse(cr, 1, [line.move_mirror_rel_id.id], context={})
                        continue
                    mirror_selected_list_ids = self.pool.get('account.multicompany.relation').search(cr, 1, [('origin_account', '=', line.account_id.id), ('origin_journal', '=', line.journal_id.id)], context=context)
                    move_id = False
                    if len(mirror_selected_list_ids) > 0:
                        mirror_selected_list = self.pool.get('account.multicompany.relation').browse(cr, 1, mirror_selected_list_ids, context=context)
    
                        for mirror in mirror_selected_list:
                            if line.account_id and line.account_id.id == mirror.origin_account.id and line.journal_id.id == mirror.origin_journal.id:
                                if mirror.origin_analytic_account:
                                    if line.analytic_account_id and line.analytic_account_id.id == mirror.origin_analytic_account:
                                        mirror_selected = mirror
                                        break
                                elif not mirror_selected:
                                    mirror_selected = mirror
                    
                        if mirror_selected:
                            origin_journal = mirror_selected.origin_journal
                            origin_account = mirror_selected.origin_account
                            targ_journal =  mirror_selected.targ_journal
                            targ_account = mirror_selected.targ_account
                        else:
                            return result
                                
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
                                'name':'MCR: ' + original_move.name,
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
                        self.pool.get('account.move.line').write(cr, uid, [line.id], {'move_mirror_rel_id' : move_id})
        
                        analytic_account_id = ''
                        if line.analytic_account_id and line.analytic_account_id == mirror_selected.origin_analytic_account:
                            analytic_account_id = mirror_selected.targ_analytic_account.id
        
                        move_line_one = {
                                         'name':line.name,
                                         'debit':line.credit,
                                         'credit':line.debit,
                                         'account_id':targ_account.id,
                                         'move_id': move_id,
                                         'amount_currency':line.amount_currency * -1,
                                         'period_id':move_period or False,
                                         'journal_id':targ_journal.id,
                                         'partner_id':line.partner_id.id,
                                         'currency_id':line.currency_id.id,
                                         'date_maturity':line.date_maturity,
                                         'date':line.date,
                                         'date_created':line.date_created,
                                         'state':'valid',
                                         'analytic_account_id':analytic_account_id,
                                         'company_id':targ_account.company_id.id,
                                         }
        
                        self.pool.get('account.move.line').create(cr, 1, move_line_one)
                        if line.debit != 0.0:
                            move_line_two_account_id = targ_journal.default_credit_account_id
                        else:
                            move_line_two_account_id = targ_journal.default_debit_account_id
        
                        move_line_two = {
                                         'name':line.name,
                                         'debit':line.debit,
                                         'credit':line.credit,
                                         'account_id':move_line_two_account_id.id,
                                         'move_id': move_id,
                                         'amount_currency':line.amount_currency,
                                         'journal_id':targ_journal.id,
                                         'period_id':move_period or False,
                                         'partner_id':line.partner_id.id,
                                         'currency_id':line.currency_id.id,
                                         'date_maturity':line.date_maturity,
                                         'date':line.date,
                                         'date_created':line.date_created,
                                         'state':'valid',
                                         'analytic_account_id':analytic_account_id,
                                         'company_id':targ_account.company_id.id,
                                         }
                        self.pool.get('account.move.line').create(cr, 1, move_line_two)
                        
                        #Posted mirror
                        self.pool.get('account.move').post(cr, 1, [move_id], context={})
                    if move_id and original_move.move_reverse_id:
                        self.pool.get('account.move').reverse(cr, 1, [move_id], context={})
        return result
    
    def unlink(self, cr, uid, ids, context=None, check=True):
        for move in self.browse(cr, 1, ids, context=context):
            for line in move.line_id:
                if line.move_mirror_rel_id:
                    self.pool.get('account.move').button_cancel(cr, 1, [line.move_mirror_rel_id.id])
                    result = super(account_move, self).unlink(cr, 1, [line.move_mirror_rel_id.id], context=context, check=check)
        result = super(account_move, self).unlink(cr, 1, ids, context=context, check=check)
        return result
