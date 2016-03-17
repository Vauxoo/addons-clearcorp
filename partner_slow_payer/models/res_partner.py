# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from datetime import date
from openerp.exceptions import Warning


class ResPartner(models.Model):

    _inherit = 'res.partner'

    slow_payer = fields.Boolean('Slow payer', compute='_compute_slow_payer')

    @api.multi
    def _compute_slow_payer(self):
        today = date.today().strftime('%d-%m-%Y')
        for partner in self:
            invoice = self.env['account.invoice'].search(
                [('partner_id', '=', partner.id),
                 ('date_due', '<', today),
                 ('state', '=', 'open')])
            if invoice:
                partner.slow_payer = True
                return True
            else:
                return False


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        if self.partner_id.slow_payer:
            raise Warning('You have a pending invoice')
        elif self.partner_id.credit_limit == 0.0:
            raise Warning('You credit is in cero')
        else:
            return self.write({'state': 'open'})


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def action_wait(self):
        super(SaleOrder, self).action_wait()
        if self.partner_id.credit_limit == 0.0:
            raise Warning('You credit is in cero')
        elif self.partner_id.slow_payer:
            raise Warning('You have a pending invoice')
