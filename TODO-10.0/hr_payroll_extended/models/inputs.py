# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class InputValue(models.Model):

    _name = 'hr.payroll.extended.input.value'
    _rec_name = 'code'

    code = fields.Char(size=8)
    type = fields.Selection(
        [('worked_days', 'Worked Days'),
         ('other_inputs', 'Other Inputs')], string='Type')


class WorkedDays(models.Model):

    _inherit = 'hr.payslip.worked_days'

    @api.onchange('work_code')
    def onchange_work_code(self):
        if self.work_code:
            self.code = self.work_code.code
        else:
            self.code = ''

    work_code = fields.Many2one(
        'hr.payroll.extended.input.value', string='Code',
        ondelete='restrict', domain=[('type', '=', 'worked_days')])


class Input(models.Model):

    _inherit = 'hr.payslip.input'

    @api.onchange('input_code')
    def onchange_input_code(self):
        if self.input_code:
            self.code = self.input_code.code
        else:
            self.code = ''

    input_code = fields.Many2one(
        'hr.payroll.extended.input.value', string='Code',
        ondelete='restrict', domain=[('type', '=', 'other_inputs')])
