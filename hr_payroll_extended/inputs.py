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

from openerp import models, fields


class InputValue(models.Model):

    _name = 'hr.payroll.extended.input.value'
    _rec_name = 'code'

    code = fields.Char(size=8)
    type = fields.Selection(
        [('worked_days', 'Worked Days'),
         ('other_inputs', 'Other Inputs')], string='Type')


class WorkedDays(models.Model):

    _inherit = 'hr.payslip.worked_days'

    def _compute_work_code(self):
        for worked_day in self:
            if worked_day.code:
                value = self.env[
                        'hr.payroll.extended.input.value'
                    ].search(
                        [('code', '=', worked_day.code),
                         ('type', '=', 'worked_days')])
                worked_day.work_code = value.id
            else:
                worked_day.work_code = False

    def _inverse_work_code(self):
        for worked_day in self:
            worked_day.code = worked_day.work_code.code

    work_code = fields.Many2one(
        'hr.payroll.extended.input.value', compute='_compute_work_code',
        inverse='_inverse_work_code', string='Code',
        domain=[('type', '=', 'worked_days')])


class Input(models.Model):

    _inherit = 'hr.payslip.input'

    def _compute_input_code(self):
        for item in self:
            if item.code:
                value = self.env[
                        'hr.payroll.extended.input.value'
                    ].search(
                        [('code', '=', item.code),
                         ('type', '=', 'other_inputs')])
                item.input_code = value.id
            else:
                item.input_code = False

    def _inverse_input_code(self):
        for item in self:
            item.code = item.input_code.code

    input_code = fields.Many2one(
        'hr.payroll.extended.input.value', compute='_compute_input_code',
        inverse='_inverse_input_code', string='Code',
        domain=[('type', '=', 'other_inputs')])
