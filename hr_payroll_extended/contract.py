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

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class Contract(models.Model):

    _inherit = 'hr.contract'

    use_fixed_working_hours = fields.Boolean('Use Work Hours')
    fixed_working_hours = fields.Float(
        'Work Hours', digits=dp.get_precision('Payroll'))
    fixed_working_days = fields.Float(
        'Work Days', digits=dp.get_precision('Payroll'))
    fixed_working_hours_code = fields.Many2one(
        'hr.payroll.extended.input.value', string='Code',
        domain=[('type', '=', 'worked_days')])
