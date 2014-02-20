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
            
            exp_lines = exp.line_ids
            taxes_per_line = self.tax_per_exp_line(cr, uid, exp_lines, context=context)
            acc_move = exp.account_move_id
            assigned_exp_lines = [] #list of associated expense lines with account move lines
            assigned_tax_exp_lines = [] #list of expense lines whose tax has been associated with account move lines
            for acc_move_line in acc_move.line_id:
                for exp_line in exp_lines:
                    exp_acc = exp_line.product_id.property_account_expense or exp_line.product_id.categ_id.property_account_expense_categ
                    exp_name = exp_line.name
                    exp_amount = exp_line.total_amount
                    acc_move_line_amount = abs(acc_move_line.debit - acc_move_line.credit) or abs(acc_move_line.amount_currency)
                    
                    if exp_name.find(acc_move_line.name) != -1 and exp_amount == acc_move_line_amount and \
                    exp_acc.id == acc_move_line.account_id.id  and exp_line.id not in assigned_exp_lines:
                        bud_move_id = mov_line_obj.search(cr, uid, [('expense_line_id','=',exp_line.id)], context=context)[0]
                        if bud_move_id:
                            mov_line_obj.write(cr ,uid, [bud_move_id], {'move_line_id':acc_move_line.id})
                            assigned_exp_lines.append(exp_line.id)
                    if not acc_move_line.product_id: 
                        if exp_line.id not in assigned_tax_exp_lines:
                            exp_line_taxes = taxes_per_line.get(exp_line.id,[])
                            for tax_amount in exp_line_taxes:
                                fixed_amount = abs(acc_move_line.debit - acc_move_line.credit) or abs(acc_move_line.amount_currency)
                                if fixed_amount == tax_amount:                                    
                                    bud_line = mov_line_obj.create(cr, uid, {'budget_move_id': exp_line.expense_id.budget_move_id.id,
                                                 'origin' : _('Tax of: ') + exp_line.name[:54],
                                                 'program_line_id': exp_line.program_line_id.id,
                                                 'fixed_amount': abs(acc_move_line.debit - acc_move_line.credit) or abs(acc_move_line.amount_currency),
                                                 #'expense_line_id': line_id,
                                                 'move_line_id': acc_move_line.id,
                                                 'account_move_id': acc_move.id
                                                  }, context=context)
                                    assigned_tax_exp_lines.append(exp_line.id)
                            
        return result
                
    def tax_per_exp_line(self, cr, uid, expense_lines, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        mapping = {}
        
        if context is None:
            context = {}

        for line in expense_lines:
            exp = line.expense_id
            company_currency = exp.company_id.currency_id.id
            ###
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            ###
            tax_code_found= False
            
            #Calculate tax according to default tax on product
            taxes = []
            #Taken from product_id_onchange in account.invoice
            if line.product_id:
                fposition_id = False
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
                product = line.product_id
                taxes = product.supplier_taxes_id
                #If taxes are not related to the product, maybe they are in the account
                if not taxes:
                    a = product.property_account_expense.id
                    if not a:
                        a = product.categ_id.property_account_expense_categ.id
                    a = fpos_obj.map_account(cr, uid, fpos, a)
                    taxes = a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False
                tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
            if not taxes:
                continue
            #Calculating tax on the line and creating move?
            for tax in tax_obj.compute_all(cr, uid, taxes,
                    line.unit_amount ,
                    line.unit_quantity, line.product_id,
                    exp.user_id.partner_id)['taxes']:
                
                line_tax_amounts =[]
                
                tax_code_id = tax['base_code_id']
                tax_amount = line.total_amount * tax['base_sign']
                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True
                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, exp.currency_id.id, company_currency, tax_amount, context={'date': exp.date_confirm})
                ## 
                is_price_include = tax_obj.read(cr,uid,tax['id'],['price_include'],context)['price_include']
                if is_price_include:
                    ## We need to deduce the price for the tax
                    res[-1]['price'] = res[-1]['price']  - (tax['amount'] * tax['base_sign'] or 0.0)
                assoc_tax = {
                             'type':'tax',
                             'name':tax['name'],
                             'price_unit': tax['price_unit'],
                             'quantity': 1,
                             'price':  tax['amount'] * tax['base_sign'] or 0.0,
                             'account_id': tax['account_collected_id'] or mres['account_id'],
                             'tax_code_id': tax['tax_code_id'],
                             'tax_amount': tax['amount'] * tax['base_sign'],
                             }
                line_tax_amounts.append(assoc_tax['tax_amount'])
                res.append(assoc_tax)
            mapping[line.id]=line_tax_amounts
        return mapping
        
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
        if program_line:
            for line in self.pool.get('budget.program.line').browse(cr, uid,[program_line], context=context):
                return {'value': {'line_available':line.available_budget},}
        return {'value': {}}
    
    def _check_no_taxes(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            product = line.product_id
            if product.supplier_taxes_id:
                return False
            if product.property_account_expense and product.property_account_expense.tax_ids:
                return False
            elif product.categ_id.property_account_expense_categ and product.categ_id.property_account_expense_categ.tax_ids:
                return False
        return True
    
    def _check_available(self, cr, uid, ids, field_name, args, context=None):
        bud_line_obj = self.pool.get('budget.move.line')
        result ={}
        if ids: 
            for exp_line_id in ids:    
                bud_line_ids = bud_line_obj.search(cr, uid, [('expense_line_id','=', exp_line_id)], context=context)
                for bud_line in bud_line_obj.browse(cr, uid,bud_line_ids, context=context):
                    result[exp_line_id] = bud_line.program_line_id.available_budget
        return result
    
    _columns = {'program_line_id': fields.many2one('budget.program.line', 'Program line', ),
                'line_available': fields.function(_check_available,  type='float', method=True, string='Line available',readonly=True),
                }
    
    _constraints=[
        (_check_no_taxes, 'Error!\n There is a tax defined for this product, its account or the account of the product category. \n The tax must be included in the price of the expense product.', []),
        ]
    
    def create_budget_move_line(self, cr, uid, line_id, context=None):
        exp_obj = self.pool.get('hr.expense.expense')
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
        
