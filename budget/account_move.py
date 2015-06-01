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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class accountMove(orm.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']
    
    OPTIONS = [
        ('void', 'Voids budget move'),
        ('budget', 'Budget move'),
    ]
    
    _columns = {
        'budget_move_id': fields.many2one('budget.move', 'Budget move'),
        'budget_type': fields.selection(OPTIONS, 'budget_type', readonly=True),
    }
    
    def copy(self, cr, uid, id, default, context=None):
       default = {} if default is None else default.copy()
       default.update({
            'budget_move_id':False
        })
       return super(accountMove, self).copy(cr, uid, id, default, context)
    
    def check_moves_budget(self, cr, uid, ids, context=None):
        moves = self.browse(cr, uid, ids, context=context)
        res = False
        for move in moves:
            for move_line in move.line_id:
                if move_line.budget_program_line:
                    return True
        return res
    
    def create_budget_moves(self, cr, uid, ids, context=None):
        bud_mov_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        acc_mov_obj = self.pool.get('account.move')
        moves = self.browse(cr, uid, ids, context=context)
        created_move_ids =[] 
        for move in moves:
            if self.check_moves_budget(cr, uid, [move.id], context=context):
                bud_move_id = bud_mov_obj.create(cr, uid, { 'type':'manual' ,'origin':move.name}, context=context)
                acc_mov_obj.write(cr, uid, [move.id], {'budget_type': 'budget', 'budget_move_id':bud_move_id}, context=context)
                created_move_ids.append(bud_move_id)
                for move_line in move.line_id:
                    if move_line.budget_program_line:
                        amount = 0.0
                        if move_line.credit > 0.0:
                            amount = move_line.credit *-1
                        if move_line.debit > 0.0:
                            amount = move_line.debit
                        new_line_id=bud_line_obj.create(cr, uid, {'budget_move_id': bud_move_id,
                                             'origin' : move_line.name,
                                             'program_line_id': move_line.budget_program_line.id, 
                                             'fixed_amount': amount,
                                             'move_line_id': move_line.id,
                                              }, context=context)
                bud_mov_obj.signal_workflow(cr, uid, [bud_move_id], 'button_execute', context=context)
                bud_mov_obj.recalculate_values(cr, uid, [bud_move_id], context=context)
        return created_move_ids
    
    def rewrite_bud_move_names(self, cr, uid, acc_ids, context=None):
        bud_mov_obj = self.pool.get('budget.move')
        acc_mov_obj = self.pool.get('account.move')
        moves = self.browse(cr, uid, acc_ids, context=context) 
        for move in moves:
            if move.budget_move_id:
                bud_mov_obj.write(cr, uid, [move.id],{'origin' : move_line.name,})
 
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        
        obj_sequence = self.pool.get('ir.sequence')
        
        created_move_ids =  self.create_budget_moves(cr, uid, ids, context=context)
        #=============================================================================#
        check_lines = []
        next_step = False
        amount = 0.0
        percentage = 0.0
        obj_move_line = self.pool.get('account.move.line')
        
        #Check if this account.move has distributions lines and check (only in valid_moves -> is a account.move object)
        for move in self.browse(cr, uid, valid_moves, context=context):
            move_lines = obj_move_line.search(cr, uid, [('move_id','=',move.id)])
            
            for line in obj_move_line.browse(cr, uid, move_lines):
                if line.account_id.moves_cash:
                     check_lines.append(line)
        
            #Check amount in line.distribution (if there exist any line.id)
            if len(check_lines) > 0:
                for line in check_lines: 
                    distribution_lines = self.pool.get('account.move.line.distribution').search(cr, uid, [('account_move_line_id', '=', line.id)])
                    
                    if len(distribution_lines) > 0:
                        #Sum distribution_amount. This amount is equal to line.amount (debit or credit).
                        for distribution in self.pool.get('account.move.line.distribution').browse(cr, uid, distribution_lines):
                            amount += distribution.distribution_amount
                            percentage += distribution.distribution_percentage
                        
                        #Find amount (debit or credit) and compare. 
                        if line.debit > 0:
                            amount_check = line.debit
                        else:
                            amount_check = line.credit
                        
                        #Continue with normal process
                        if (amount_check == amount) and (percentage == 100):                        
                            next_step = True
                            
                        else:
                            next_step = False
                            return {'value': {'account_move_line_id': line.id},
                                    'warning':{'title':'Warning','message':'Distribution amount for this move line does not match with original amount line'}}
    
                    #Continue with normal process
                    else:
                        next_step = True
            
            else:
                next_step = True
            
            #=============================================================================#
            if next_step:
                for move in self.browse(cr, uid, valid_moves, context=context):
                    if move.name =='/':
                        new_name = False
                        journal = move.journal_id
        
                        if invoice and invoice.internal_number:
                            new_name = invoice.internal_number
                        else:
                            if journal.sequence_id:
                                c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                                new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                            else:
                                raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
                        
                        if new_name:
                            self.write(cr, uid, [move.id], {'name':new_name})
        
                cr.execute('UPDATE account_move '\
                           'SET state=%s '\
                           'WHERE id IN %s',
                           ('posted', tuple(valid_moves),))
        super_result = super(accountMove, self).post(cr, uid, ids, context=context)
        self.rewrite_bud_move_names(cr, uid, ids, context=context)
        return super_result

    def button_cancel(self, cr, uid, ids, context=None):
        amld_obj=self.pool.get('account.move.line.distribution')
        bud_mov_obj=self.pool.get('budget.move')
        for acc_move in self.browse(cr, uid, ids, context=context):
            bud_move_id = acc_move.budget_move_id.id
            if bud_move_id:
                bud_mov_obj.signal_workflow(cr, uid, [bud_move_id], 'button_cancel', context=context)
                bud_mov_obj.signal_workflow(cr, uid, [bud_move_id], 'button_draft', context=context)
                bud_mov_obj.unlink(cr, uid, [bud_move_id], context=context)        
        super(accountMove, self).button_cancel(cr, uid, ids, context=context)
        return True    