# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
import openerp.addons.decimal_precision as dp


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
