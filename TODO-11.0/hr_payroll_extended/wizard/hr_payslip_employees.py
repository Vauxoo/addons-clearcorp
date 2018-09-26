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

from odoo import api, fields, models, _


class hr_payslip_employees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    @api.multi
    def compute_sheet(self):
        run_pool = self.env['hr.payslip.run']
        active_id=self.env.context.get('active_id')
        if active_id:
            [run_data] = run_pool.browse(active_id).read(['date'])
        date = run_data.get('date')
        if date:
            return super(hr_payslip_employees, self.with_context(date=date)).compute_sheet()
        return super(hr_payslip_employees, self).compute_sheet()
