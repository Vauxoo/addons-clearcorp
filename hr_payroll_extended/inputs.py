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
