# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class HRContract(models.Model):
    _inherit = 'hr.contract'

    currency_id = fields.Many2one('res.currency', string='Currency')


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    currency_id = fields.Many2one('res.currency', compute='_compute_currency',
                                  string='Currency')

    @api.depends('contract_id')
    def _compute_currency(self):
        self.currency_id = self.contract_id.currency_id
