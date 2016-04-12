# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
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
            else:
                partner.slow_payer = False


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if not self.env.user.has_group(
                    'partner_slow_payer.group_partner_slow_payer'):
                if invoice.partner_id.slow_payer:
                    raise Warning(_('You have a pending invoice'))
                if invoice.partner_id.credit_limit - invoice.partner_id.credit - \
                        invoice.amount_total <= 0.0:
                    raise Warning(_('You credit is in cero'))
        super(AccountInvoice, self).invoice_validate()


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def action_wait(self):
        super(SaleOrder, self).action_wait()
        for sale in self:
            if not self.env.user.has_group(
                    'partner_slow_payer.group_partner_slow_payer'):
                if sale.partner_id.credit_limit - sale.partner_id.credit - \
                        sale.amount_total <= 0.0:
                    raise Warning(_('You credit is in cero'))
                if sale.partner_id.slow_payer:
                    raise Warning(_('You have a pending invoice'))
