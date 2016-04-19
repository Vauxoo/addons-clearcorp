# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SalaryRule(models.Model):

    _RULE_TYPES = [
        ('partner', 'Partner'),
        ('employee', 'Employee'),
    ]

    _inherit = 'hr.salary.rule'
    rule_type_credit = fields.Selection(
        _RULE_TYPES, string='Credit Rule Type', default='employee'),
    rule_type_debit = fields.Selection(
        _RULE_TYPES, string='Debit Rule Type', default='employee'),
    res_partner_credit = fields.Many2one(
        'res.partner', string='Credit Partner'),
    res_partner_debit = fields.Many2one(
        'res.partner', string='Debit Partner'),


class PaySlip(models.Model):

    _inherit = 'hr.payslip'

    @api.multi
    def process_sheet(self):
        res = super(PaySlip, self).process_sheet()
        for payslip in self:
            for line in payslip.line_ids:
                if line.salary_rule_id:
                    # Check is salary rule has debit
                    if line.salary_rule_id.account_debit:
                        # Check if rule has rule_type_debit
                        if line.salary_rule_id.rule_type_debit:
                            move_line = self.env['account.move.line']
                            # Check the rule_type if partner
                            if line.salary_rule_id.rule_type_debit ==\
                                    'partner':
                                move_lines = move_line.search(
                                    [('move_id', '=', payslip.move_id.id),
                                     ('debit', '=', line.total),
                                     ('account_id', '=',
                                      line.salary_rule_id.account_debit.id)])
                                if move_lines:
                                    _rule = line.salary_rule_id
                                    _partner = _rule.res_partner_debit.id
                                    move_lines.write(
                                        {
                                            'partner_id': _partner
                                        })
                            # Rule type is employee
                            else:
                                move_lines = move_line.search(
                                    [('move_id', '=', payslip.move_id.id),
                                     ('debit', '=', line.total),
                                     ('account_id', '=',
                                      line.salary_rule_id.account_debit.id)])
                                if move_lines:
                                    _employee = payslip.employee_id
                                    _id = _employee.address_home_id.id
                                    move_lines.write(
                                        {
                                            'partner_id': _id
                                        })
                    # Credit check if salary rule has credit
                    if line.salary_rule_id.account_credit:
                        # Check if rule has rule_type credit
                        if line.salary_rule_id.rule_type_credit:
                            move_line = self.env['account.move.line']
                            # Check if rule_type is partner
                            if line.salary_rule_id.rule_type_credit ==\
                                    'partner':
                                move_lines = move_line.search(
                                    [('move_id', '=', payslip.move_id.id),
                                     ('credit', '=', line.total),
                                     ('account_id', '=',
                                      line.salary_rule_id.account_credit.id)],)
                                if move_lines:
                                    _rule = line.salary_rule_id
                                    _partner = _rule.res_partner_credit.id
                                    move_lines.write(
                                        {
                                            'partner_id': _partner})
                            # Rule type is employee
                            else:
                                move_lines = move_line.search(
                                    [('move_id', '=', payslip.move_id.id),
                                     ('credit', '=', line.total),
                                     ('account_id', '=',
                                      line.salary_rule_id.account_credit.id)])
                                if move_lines:
                                    _employee = payslip.employee_id
                                    _id = _employee.address_home_id.id
                                    move_lines.write(
                                        {
                                            'partner_id': _id
                                        })
        return res
