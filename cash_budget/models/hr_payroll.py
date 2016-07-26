# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api


class HRSalaryRule(models.Model):

    _inherit = 'hr.salary.rule'

    debit_budget_program_line = fields.Many2one(
        'cash.budget.program.line', string='Debit Budget Program Line')
    credit_budget_program_line = fields.Many2one(
        'cash.budget.program.line', string='Credit Budget Program Line')


class HRPayslip(models.Model):

    _inherit = 'hr.payslip'

    budget_move_id = fields.Many2one('cash.budget.move', 'Budget move')

    @api.multi
    def process_sheet(self):
        obj_bud_mov = self.env['cash.budget.move']
        obj_bud_line = self.env['cash.budget.move.line']
        for payslip in self:
            payslip_total = 0.0
            bud_move_id = obj_bud_mov.create(
                {'origin': payslip.name, 'type': 'payroll'})
            payslip.write({'budget_move_id': bud_move_id.id})
        result = super(HRPayslip, self).process_sheet()

        for payslip in self:
            account_move = payslip.move_id
            bud_move = payslip.budget_move_id
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
                    rule = payslip_line.salary_rule_id
                    if is_debit:
                        payslip_line_debit_account_id =\
                            rule.account_debit.id
                        payslip_line_credit_account_id = None
                        if not rule.debit_budget_program_line:
                            continue
                        payslip_line_debit_budget_program_id =\
                            rule.debit_budget_program_line.id
                        payslip_line_credit_budget_program_id = None
                    else:
                        payslip_line_debit_account_id = None
                        payslip_line_credit_account_id = rule.account_credit.id
                        if not rule.credit_budget_program_line:
                            continue
                        payslip_line_debit_budget_program_id = None
                        payslip_line_credit_budget_program_id =\
                            rule.credit_budget_program_line.id

                    payslip_line_name = payslip_line.name
                    if move_line_name != payslip_line_name:
                        continue
                    vals = {
                        'origin': payslip_line.name,
                        'budget_move_id': bud_move.id,
                        'payslip_line_id': payslip_line.id,
                        'move_line_id': move_line.id
                    }
                    if not is_debit and\
                            payslip_line_credit_account_id ==\
                            move_line_account_id and\
                            payslip_line_credit_budget_program_id:
                        payslip_total += move_line_credit
                        vals['fixed_amount'] = move_line_credit * -1
                        vals['program_line_id'] =\
                            payslip_line_credit_budget_program_id
                    if is_debit and\
                            payslip_line_debit_account_id ==\
                            move_line_account_id and\
                            payslip_line_debit_budget_program_id:
                        payslip_total += move_line_debit
                        vals['fixed_amount'] = move_line_debit
                        vals['program_line_id'] =\
                            payslip_line_debit_budget_program_id
                    obj_bud_line.create(vals)
            bud_move.write({'fixed_amount': payslip_total})
            bud_move.signal_workflow('button_reserve')
            bud_move.signal_workflow('button_compromise')
            bud_move.signal_workflow('button_execute')
        return result
