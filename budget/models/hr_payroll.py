# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.osv import fields, osv

class hrSalaryruleInherit(osv.osv):
    
    _inherit = 'hr.salary.rule'
    
    _columns = {
        'debit_budget_program_line': fields.many2one('budget.program.line','Debit Budget Program Line', ),
        'credit_budget_program_line': fields.many2one('budget.program.line','Credit Budget Program Line',)
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
                
                if move_line.debit:
                    is_debit = True
                else:
                    is_debit = False

                for payslip_line in payslip.line_ids:
                        if is_debit:
                            payslip_line_debit_account_id = payslip_line.salary_rule_id.account_debit.id
                            payslip_line_credit_account_id = None
                            if not payslip_line.salary_rule_id.debit_budget_program_line:
                                continue
                            payslip_line_debit_budget_program_id = payslip_line.salary_rule_id.debit_budget_program_line.id
                            payslip_line_credit_budget_program_id = None
                        else:
                            payslip_line_debit_account_id = None
                            payslip_line_credit_account_id = payslip_line.salary_rule_id.account_credit.id
                            if not payslip_line.salary_rule_id.credit_budget_program_line:
                                continue
                            payslip_line_debit_budget_program_id = None
                            payslip_line_credit_budget_program_id = payslip_line.salary_rule_id.credit_budget_program_line.id

                        payslip_line_amount = payslip_line.total
                        payslip_line_name = payslip_line.name
                        

                        print payslip_line_amount
                        print move_line_debit
                        print move_line_credit
                        
                        if move_line_name != payslip_line_name :
                            continue
                             
                         
                        if not is_debit and\
                         payslip_line_credit_account_id == move_line_account_id and\
                         payslip_line_credit_budget_program_id:
                            vals={}
                            payslip_total+= move_line_credit
                            vals['fixed_amount'] = move_line_credit * -1
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
                            payslip_total+= move_line_debit
                            vals['fixed_amount'] = move_line_debit
                            vals['program_line_id'] = payslip_line_debit_budget_program_id
                            vals['origin'] = payslip_line.name
                            vals['budget_move_id'] = bud_move_id
                            vals['payslip_line_id'] = payslip_line.id
                            vals['move_line_id'] = move_line.id
                            obj_bud_line.create(cr, uid, vals, context=context )
            obj_bud_mov.write(cr, uid, [bud_move_id], {'fixed_amount':payslip_total}, context=context)
            obj_bud_mov.signal_workflow(cr, uid, [bud_move_id], 'button_compromise', context=context)
            obj_bud_mov.signal_workflow(cr, uid, [bud_move_id], 'button_execute', context=context)
        return result