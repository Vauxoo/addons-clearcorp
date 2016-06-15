# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class Invoice(models.Model):

    _inherit = 'account.invoice'
    _name = 'account.invoice'

    @api.onchange('force_commission')
    def onchange_force_commission(self):
        self.commission_percentage = 0.0
        self.post_expiration_days = 0.0

    force_commission = fields.Boolean(
        'Force Commission', help='Check if you want to '
        'pay a fixed commission percentage for this invoice.')
    commission_percentage = fields.Float(
        'Commission', digits=dp.get_precision('Account'))
    post_expiration_days = fields.Integer(
        'Post-Expiration Days', help='Quantity of days '
        'of tolerance between the invoice due date and the payment date.')
