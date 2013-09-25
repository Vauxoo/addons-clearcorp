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
from tools.translate import _
from osv import fields, osv
import netsvc
import decimal_precision as dp

class hr_expense_expense(osv.osv):
    _name = "hr.expense.expense"
    _inherit = 'hr.expense.expense'
    
    _columns = {
                'budget_move_id': fields.many2one('budget.move', 'Budget move', readonly=True, ),            
                }
    
    
    def create_budget_move_line(self, cr, uid, line_id, context=None):    
        exp_obj = self.pool.get('hr.expense.expense')
       # acc_move_obj = self.pool.get('account.move')
        exp_line_obj = self.pool.get('hr.expense.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        fixed_amount = 0.0
        expense_line = exp_line_obj.browse(cr, uid, [line_id], context=context)[0]
        expense = exp_obj.browse(cr, uid, [expense_line.expense_id.id], context=context)[0]
        move_id = expense.budget_move_id.id        
        fixed_amount = expense_line.total_amount     
        bud_line = bud_line_obj.create(cr, uid, {'budget_move_id': move_id,
                                         'origin' : expense_line.name,
                                         'program_line_id': expense_line.program_line_id.id,
                                         'fixed_amount': fixed_amount ,
                                         'expense_line_id': line_id,
                                        # 'account_move_id': expense.move_id.id
                                          }, context=context)
        return bud_line
    
    
    def create(self, cr, uid, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        exp_id = super(hr_expense_expense,self).create(cr, uid, vals, context=None)
        move_id = self.create_budget_move(cr, uid, [exp_id], context)
        self.write(cr, uid, [exp_id], {'budget_move_id':move_id }, context)
        expense_amount=0.0
        for expense in self.browse(cr, uid, [exp_id], context):
            expense_amount = expense.amount
            for line in expense.line_ids:
                created_line_id = self.create_budget_move_line(cr, uid, line.id, context=context)
        bud_move_obj.write(cr, uid, [move_id], {'fixed_amount': expense_amount})
        bud_move_obj._workflow_signal(cr, uid, [move_id], 'button_reserve', context=context)
        return exp_id
        
    def write(self, cr, uid, ids, vals, context=None):        
        bud_move_obj = self.pool.get('budget.move')
        result = super(hr_expense_expense, self).write(cr, uid, ids, vals, context=context)
        for exp in self.browse(cr, uid, ids, context=context):
            if exp.budget_move_id and exp.budget_move_id.state !='draft':
                bud_move_obj.write(cr, uid, [exp.budget_move_id.id], {'fixed_amount':exp.amount})
                bud_move_obj.recalculate_values(cr, uid, [exp.budget_move_id.id], context=context)
        return result   
        
    def create_budget_move(self,cr, uid, ids, context=None):
        bud_move_obj = self.pool.get('budget.move')
        move_id = bud_move_obj.create(cr, uid, { 'type': 'expense' }, context=context)
        return move_id
 
    def expense_confirm(self, cr, uid, ids, context=None):
        bud_move_obj = self.pool.get('budget.move')
        for exp in self.browse(cr, uid, ids, context=context) :
            super(hr_expense_expense,self).expense_confirm(cr, uid, [exp.id], context=context)
            
            move_id = exp.budget_move_id.id
            self.write(cr, uid, [exp.id], {'budget_move_id' : move_id})
            
    def expense_canceled(self, cr, uid, ids, context=None):
        bud_move_obj = self.pool.get('budget.move')
        exp_id = super(hr_expense_expense,self).expense_canceled(cr, uid, ids, context=context)
        for expense in self.browse(cr, uid, ids, context=context):
            bud_move_obj._workflow_signal(cr, uid, [expense.budget_move_id.id], 'button_cancel', context=context)
            bud_move_obj.recalculate_values(cr, uid, [expense.budget_move_id.id], context=context)
    
    def expense_draft(self, cr, uid, ids, context=None):
        bud_move_obj = self.pool.get('budget.move')
        self.write(cr, uid, ids, {'state': 'draft'},context=context)
        for expense in self.browse(cr, uid, ids, context=context):
            if expense.budget_move_id:
                bud_move_obj._workflow_signal(cr, uid, [expense.budget_move_id.id], 'button_draft', context=context)
                bud_move_obj._workflow_signal(cr, uid, [expense.budget_move_id.id], 'button_reserve', context=context)
                bud_move_obj.recalculate_values(cr, uid, [expense.budget_move_id.id], context=context)
                
    def action_receipt_create(self, cr, uid, ids, context=None):
        mov_line_obj = self.pool.get('budget.move.line')
        bud_move_obj = self.pool.get('budget.move')
        acc_move_obj = self.pool.get('account.move')
        
        result = super(hr_expense_expense, self).action_receipt_create(cr, uid, ids, context=context)
        for exp in self.browse(cr, uid, ids, context=context):
            acc_move_id = exp.account_move_id.id
            acc_move_obj.write(cr , uid, [acc_move_id], {'budget_type': 'budget'}, context=context)
            for bud_mov_line in exp.budget_move_id.move_lines:
                mov_line_obj.write(cr, uid, [bud_mov_line.id], {'account_move_id' : acc_move_id}, context=context)
            bud_move_obj._workflow_signal(cr, uid, [exp.budget_move_id.id], 'button_compromise', context=context)
            bud_move_obj._workflow_signal(cr, uid, [exp.budget_move_id.id], 'button_execute', context=context)
        return result
                
            
            
#    def expense_accept(self, cr, uid, ids, context=None):        
#        bud_move_obj = self.pool.get('budget.move')
#        for exp in self.browse(cr, uid, ids, context=context) :
#            super(hr_expense_expense,self).expense_accept(cr, uid, [exp.id], context=context)
#            move_id = exp.budget_move_id.id 
#            bud_move_obj._workflow_signal(cr, uid, [move_id], 'button_reserve', context=context)   
    
#    def on_change_currency(self, cr, uid, ids, currency_id, context=None):
#        if ids:
#            return {'value': {},
#                    'warning':{'title':'Warning','message':'Budget uses the currency of the company, if you use other, you should change the unit price'}}
#        else:
#            return {'value': {}}
#        
    def on_change_currency(self, cr, uid, ids, currency_id, context=None):
        if ids:
            return {'value': {},
                    'warning':{'title':'Warning','message':'Budget uses the currency of the company, if you use other, you should change the unit price'}}
        else:
            return {'value': {}}     
    
class hr_expense_line(osv.osv):
    _name = "hr.expense.line"
    _inherit = 'hr.expense.line'
    
    def on_change_program_line(self, cr, uid, ids, program_line, context=None):
        for line in self.pool.get('budget.program.line').browse(cr, uid,[program_line], context=context):
            return {'value': {'line_available':line.available_budget},}
        return {'value': {}}
    
    def _check_available(self, cr, uid, ids, field_name, args, context=None):
        bud_line_obj = self.pool.get('budget.move.line')
        result ={}
        if ids: 
            for exp_line_id in ids:    
                bud_line_ids = bud_line_obj.search(cr, uid, [('expense_line_id','=', exp_line_id)], context=context)
                for bud_line in bud_line_obj.browse(cr, uid,bud_line_ids, context=context):
                    result[exp_line_id] = bud_line.program_line_id.available_budget    
        return result
    
#    def _set_available(self, cr, uid, ids, field_name, field_value, arg, context):
#        return True
    
    _columns = {
                'program_line_id': fields.many2one('budget.program.line', 'Program line', ),
                #'line_available':fields.float('Line available',digits_compute=dp.get_precision('Account')),
                 'line_available': fields.function(_check_available,  type='float', method=True, string='Line available',readonly=True),  
                }   
    
    def create_budget_move_line(self, cr, uid, line_id, context=None):    
        exp_obj = self.pool.get('hr.expense.expense')
       # acc_move_obj = self.pool.get('account.move')
        exp_line_obj = self.pool.get('hr.expense.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        fixed_amount = 0.0
        expense_line = exp_line_obj.browse(cr, uid, [line_id], context=context)[0]
        expense = exp_obj.browse(cr, uid, [expense_line.expense_id.id], context=context)[0]
        move_id = expense.budget_move_id.id        
        fixed_amount = expense_line.total_amount     
        bud_line = bud_line_obj.create(cr, uid, {'budget_move_id': move_id,
                                         'origin' : expense_line.name,
                                         'program_line_id': expense_line.program_line_id.id,
                                         'fixed_amount': fixed_amount ,
                                         'expense_line_id': line_id,
                                        # 'account_move_id': expense.move_id.id
                                          }, context=context)
        bud_move_obj.recalculate_values(cr, uid, [move_id], context=context)
        return bud_line
    
    
    def create(self, cr, uid, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        exp_obj = self.pool.get('hr.expense.expense')
        exp_line_id = super(hr_expense_line,self).create(cr, uid, vals, context=None)
        exp_id = vals['expense_id']
        for expense in exp_obj.browse(cr, uid, [exp_id], context=context): 
            if expense.budget_move_id:
                bud_line_id = self.create_budget_move_line(cr, uid, exp_line_id, context)
        return exp_line_id
    
    def write(self, cr, uid, ids, vals, context=None):
        bud_line_obj = self.pool.get('budget.move.line')
        bud_move_obj = self.pool.get('budget.move')
        write_result = True
        bud_line_dict = {}
        if 'unit_amount' in vals.keys() or 'program_line_id' in vals.keys() or 'name' in vals.keys():
            
            if 'unit_amount' in vals.keys():
                bud_line_dict['fixed_amount'] = vals['unit_amount']
            if 'program_line_id' in vals.keys():
                bud_line_dict['program_line_id'] = vals['program_line_id']
            if 'name' in vals.keys():
                bud_line_dict['origin'] = vals['name']
                
            for exp_line_id in ids:
                write_result = super(hr_expense_line,self).write(cr, uid, [exp_line_id], vals, context=None)
                bud_line_ids = bud_line_obj.search(cr, uid, [('expense_line_id','=',exp_line_id)])
                for bud_line in bud_line_obj.browse(cr, uid, bud_line_ids,context=context):
                    bud_line_obj.write(cr, uid, [bud_line.id], bud_line_dict, context=None)
                    result = bud_move_obj._check_values(cr, uid, [bud_line.budget_move_id.id], context=context)
                    if not result[0]:
                        raise osv.except_osv(_('Error!'), result[1])
            
        else:
            write_result=super(hr_expense_line,self).write(cr, uid, ids, vals, context=None)
        return write_result
        
        

    
    
    
    
    
    
    
    
    
    