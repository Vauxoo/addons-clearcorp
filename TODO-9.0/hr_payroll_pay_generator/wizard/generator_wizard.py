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


class GeneratorWizard(models.TransientModel):

    _name = 'hr.payroll.pay.generator.generator.wizard'

    @api.multi
    def generator_exectute(self):
        raise NotImplementedError

    pay_type_id = fields.Many2one(
        'hr.payroll.pay.generator.pay.type',
        string='Pay Type', required=True)
    payslip_run_id = fields.Many2one(
        'hr.payslip.run', string='Payslip Batch', required=True)
    salary_rule_id = fields.Many2one(
        'hr.salary.rule', string='Salary Rule', required=True)
    employee_ids = fields.Many2many(
        'hr.employee', string='Employees', required=True)
