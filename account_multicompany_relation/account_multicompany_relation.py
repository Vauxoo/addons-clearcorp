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

class AccountMulticompanyRelation(orm.Model):

    _name = "account.multicompany.relation"
    _description = "Account multicompany relation"

    _columns = {
        'name':fields.char('Name',size=64,required=True,help='Name for the mirror move relation'),
        'origin_account':fields.many2one('account.account','Origin Account',required=True,help='Indicate the origin move line account where the transaction is taking place.'),
        'targ_account':fields.many2one('account.account','Target Account',required=True,help='Indicate the target move line account that the mirror move will affect, this account can be in another company.'),
        'origin_journal':fields.many2one('account.journal','Original Journal',required=True,help='Indicate the origin journal where the transaction is taking place.'),
        'targ_journal':fields.many2one('account.journal','Target Journal',required=True,help='Indicate the target journal where the mirror move will be created, this journal can be in another company.'),
        'origin_analytic_account':fields.many2one('account.analytic.account','Origin Analytic Account',required=False,help='Indicate the origin analytic account where the transaction is taking place. Optional.'),
        'targ_analytic_account':fields.many2one('account.analytic.account','Target Analytic Account',required=False,help='Indicate the target analytic account that the mirror move line will have, this analytic account can be in another company.'),
        'mirror_move_prefix':fields.char('Move prefix',size=32,required=True,help='Prefix for the mirror move name.'),
        'inverse_debit_credit':fields.boolean('Inverse debit/credit',help='If set, the debit/credit from the origin move line will be inverted in the target move line. For example, a debit line affecting the origin account in the origin move, will result in a target move with a credit line affecting the target account on the target move.'),
        'notes':fields.text('Notes'),
    }

    _sql_constraints = [
        (
            'unique_name',
            'unique(name)',
            'The name must be unique'
        ),
    ]

    def _check_unique_mirror_relation(self, cr, uid, ids, context=None):
        for relation in self.browse(cr, uid, ids, context=context):
            relation_ids = self.search(cr, uid, [('origin_account','=',relation.origin_account.id),
                                                 ('origin_journal','=',relation.origin_journal.id),
                                                 ('origin_analytic_account','=',relation.origin_analytic_account.id)], context=context)
            if len(relation_ids) >= 2:
                return False
            elif len(relation_ids) == 1 and not relation_ids[0] == relation.id:
                return False
        return True

    _constraints = [
        (
            _check_unique_mirror_relation,
            'The same relation already exists', ['origin_account','origin_journal','origin_analytic_account']
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

class AccountMove(orm.Model):

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

        result = super(AccountMove, self).button_cancel(cr, uid, ids, context=context)
        return True

    def post(self, cr, uid, ids, context=None):
        result = super(AccountMove, self).post(cr, uid, ids, context=context)

        for move_id_original in ids:
            account_move_obj = self.pool.get('account.move')
            account_move_line_obj = self.pool.get('account.move.line')
            account_multicompany_relation_obj = self.pool.get('account.multicompany.relation')
            #Continue if this is a reversion move
            if account_move_obj.search(cr, 1, [('move_reverse_id', '=', move_id_original)], context=context):
                continue

            original_move = account_move_obj.browse(cr, 1, move_id_original, context=context)
            if original_move.line_id:
                mirror_selected = False
                for line in original_move.line_id:
                    #Test if the line already has a mirror move associated
                    if line.move_mirror_rel_id:
                        #Reverse the mirror move if the original move is reversed
                        if original_move.move_reverse_id:
                            account_move_obj.reverse(cr, 1, [line.move_mirror_rel_id.id], context={})
                        continue
                    
                    #Get parent accounts for line account
                    parent_account_ids = []                    
                    parent_account = line.account_id
                    while parent_account:
                        parent_account_ids.append(parent_account.id)
                        parent_account = parent_account.parent_id
                    analytic_account_id = line.analytic_account_id and line.analytic_account_id.id or False
                    mirror_selected_list_ids = account_multicompany_relation_obj.search(cr, 1, [('origin_account', 'in', parent_account_ids), ('origin_journal', '=', line.journal_id.id), ('origin_analytic_account', '=', analytic_account_id)], context=context)
                    move_id = False
                    if len(mirror_selected_list_ids) > 0:
                        mirror_selected_list = account_multicompany_relation_obj.browse(cr, 1, mirror_selected_list_ids, context=context)

                        mirror_selected = False

                        if len(mirror_selected_list) == 1:
                            mirror_selected = mirror_selected_list[0]
                        else:
                            mirror_index = -1
                            for mirror in mirror_selected_list:
                                if mirror_index < 0 or parent_account_ids.index(mirror.origin_account.id) < mirror_index:
                                    mirror_index = parent_account_ids.index(mirror.origin_account.id)
                                    mirror_selected = mirror

                        if mirror_selected:
                            origin_journal = mirror_selected.origin_journal
                            origin_account = mirror_selected.origin_account
                            targ_journal =  mirror_selected.targ_journal
                            targ_account = mirror_selected.targ_account
                            inverse_debit_credit = mirror_selected.inverse_debit_credit
                            mirror_move_prefix = mirror_selected.mirror_move_prefix
                        else:
                            continue

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
                            'name':mirror_move_prefix + original_move.name,
                            'ref':original_move.ref,
                            'journal_id':targ_journal.id,
                            'period_id':move_period or False,
                            'to_check':False,
                            'partner_id':original_move.partner_id.id,
                            'date':original_move.date,
                            'narration':original_move.narration,
                            'company_id':targ_account.company_id.id,
                        }
                        move_id = account_move_obj.create(cr, 1, move)
                        self.pool.get('account.move.line').write(cr, 1, [line.id], {'move_mirror_rel_id' : move_id})
        
                        analytic_account_id = ''
                        if line.analytic_account_id and line.analytic_account_id == mirror_selected.origin_analytic_account:
                            analytic_account_id = mirror_selected.targ_analytic_account.id

                        if inverse_debit_credit:
                            line_debit = line.credit
                            line_credit = line.debit
                        else:
                            line_debit = line.debit
                            line_credit = line.credit
                        move_line_one = {
                            'name':line.name,
                            'debit':line_debit,
                            'credit':line_credit,
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

                        account_move_line_obj.create(cr, 1, move_line_one)
                        if line.debit != 0.0:
                            move_line_two_account_id = targ_journal.default_credit_account_id
                        else:
                            move_line_two_account_id = targ_journal.default_debit_account_id

                        move_line_two = {
                                         'name':line.name,
                                         'debit':line_credit,
                                         'credit':line_debit,
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
                                         'analytic_account_id':False,
                                         'company_id':targ_account.company_id.id,
                                         }
                        account_move_line_obj.create(cr, 1, move_line_two)

                        #Posted mirror
                        account_move_obj.post(cr, 1, [move_id], context={})
                    if move_id and original_move.move_reverse_id:
                        account_move_obj.reverse(cr, 1, [move_id], context={})
        return result
    
    def unlink(self, cr, uid, ids, context=None, check=True):
        for move in self.browse(cr, 1, ids, context=context):
            for line in move.line_id:
                if line.move_mirror_rel_id:
                    self.pool.get('account.move').button_cancel(cr, 1, [line.move_mirror_rel_id.id])
                    result = super(AccountMove, self).unlink(cr, 1, [line.move_mirror_rel_id.id], context=context, check=check)
        result = super(AccountMove, self).unlink(cr, 1, ids, context=context, check=check)
        return result
