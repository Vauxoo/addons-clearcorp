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


class WorkedDaysValue(models.Model):

    _name = 'hr.payroll.extended.worked_days.value'
    _rec_name = 'code'

    code = fields.Char(size=8)


class WorkedDays(models.Model):

    _inherit = 'hr.payslip.worked_days'

    def _compute_work_code(self):
        for worked_day in self:
            if worked_day.code:
                value = self.env[
                        'hr.payroll.extended.worked_days.value'
                    ].search(
                        [('code', '=', worked_day.code)])
                worked_day.work_code = value.id
            else:
                worked_day.work_code = False

    def _inverse_work_code(self):
        for worked_day in self:
            worked_day.code = worked_day.work_code.code

    work_code = fields.Many2one(
        'hr.payroll.extended.worked_days.value', compute='_compute_work_code',
        inverse='_inverse_work_code', string='Code')
