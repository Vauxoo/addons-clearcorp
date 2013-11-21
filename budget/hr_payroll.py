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

from openerp.osv import fields, osv

class hrSalaryruleInherit(osv.osv):
    
    _inherit = 'hr.salary.rule'
    
    _columns = {
        'debit_budget_program_line': fields.many2one('budget.program.line','Debit Budget Program Line' ),
        'credit_budget_program_line': fields.many2one('budget.program.line','Credit Budget Program Line')
    }
    
class hr_payslip(osv.osv):

    _inherit = 'hr.payslip'
    
    _columns = {
        'budget_move_id': fields.many2one('budget.move','Budget move')
    }
    
    def process_sheet(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        obj_bud_line = self.pool.get('budget.move.line')
        for payslip in self.browse(cr, uid, ids, context=context):
            payslip_total = 0.0
            bud_move_id = obj_bud_mov.create(cr, uid, {'origin':payslip.name , 'type':'payroll'}, context=context)
            self.write(cr, uid, [payslip.id], {'budget_move_id':bud_move_id}, context=context)
        result = super(hr_payslip, self).process_sheet(cr, uid, ids, context=context)
            
        for payslip in self.browse(cr, uid, ids, context=context):
            account_move = payslip.move_id
            bud_move_id = payslip.budget_move_id.id
            assigned_payslip_lines = []
            payslip_total = 0.0
            
            for move_line in account_move.line_id: 
                move_line_debit = abs(move_line.debit)
                move_line_credit = abs(move_line.credit)
                move_line_name = move_line.name
                move_line_account_id = move_line.account_id.id
                if move_line_debit + move_line_credit == 0.0:
                    continue
                    
                for payslip_line in payslip.line_ids:
                        is_debit =False
                        payslip_line_amount = payslip_line.total
                        payslip_line_name = payslip_line.name
                        
                        if payslip_line_amount == move_line_debit:
                            is_debit =True
                        if payslip_line_amount == move_line_credit:
                            is_debit =False
                        else:
                            continue
                        
                        if move_line_name != payslip_line_name :
                            continue
                             
                        payslip_line_credit_account_id = payslip_line.salary_rule_id.account_credit.id
                        payslip_line_credit_budget_program_id = payslip_line.salary_rule_id.credit_budget_program_line.id
                        
                        payslip_line_debit_account_id = payslip_line.salary_rule_id.account_debit.id
                        payslip_line_debit_budget_program_id = payslip_line.salary_rule_id.debit_budget_program_line.id
                         
                        
                        if not is_debit and\
                         payslip_line_credit_account_id == move_line_account_id and\
                         payslip_line_credit_budget_program_id:
                            vals={}
                            payslip_total+= move_line_credit
                            vals['fixed_amount'] = move_line_credit
                            vals['program_line_id'] = payslip_line_credit_budget_program_id
                            vals['origin'] = payslip_line.name
                            vals['budget_move_id'] = bud_move_id
                            vals['payslip_line_id'] = payslip_line.id
                            vals['move_line_id'] = move_line.id
                            obj_bud_line.create(cr, uid, vals, context=context )
                            
                        if is_debit and\
                         payslip_line_debit_account_id == move_line_account_id and\
                         payslip_line_debit_budget_program_id:
                            vals={}
                            payslip_total+= abs(move_line_debit)* -1
                            vals['fixed_amount'] = move_line_credit
                            vals['program_line_id'] = payslip_line_debit_budget_program_id
                            vals['origin'] = payslip_line.name
                            vals['budget_move_id'] = bud_move_id
                            vals['payslip_line_id'] = payslip_line.id
                            vals['move_line_id'] = move_line.id
                            obj_bud_line.create(cr, uid, vals, context=context )
                            
                            
            bud_move_id = obj_bud_mov.write(cr, uid, [bud_move_id], {'fixed_amount':payslip.total}, context=context)
        ###########################
        for payslip_line in payslip.line_ids:
                if payslip_line.salary_rule_id.budget_program_line:
                    vals={}
                    payslip_total+=payslip_line.total
                    vals['fixed_amount'] = payslip_line.total
                    vals['program_line_id'] = payslip_line.salary_rule_id.budget_program_line
                    vals['origin'] = payslip_line.name
                    vals['budget_move_id'] = bud_move_id
                    vals['payslip_line_id'] = payslip_line.id
                    obj_bud_line.create(cr, uid, vals, context=context )
            bud_move_id = obj_bud_mov.write(cr, uid, [bud_move_id], {'fixed_amount':payslip.total}, context=context)
        ###
        return result
            