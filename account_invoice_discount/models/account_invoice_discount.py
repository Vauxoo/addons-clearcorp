# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class InvoiceLine(models.Model):
    """Inherits account.invoice.line
    and adds discount feature."""

    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('price_unit', 'quantity')
    def _compute_amount_line_no_discount(self):
        if self.invoice_id and self.invoice_id.currency_id:
            cur = self.invoice_id.currency_id
            self.price_subtotal_not_discounted = cur.round(
                self.price_unit * self.quantity)
        else:
            self.price_subtotal_not_discounted = \
                self.price_unit * self.quantity

    price_subtotal_not_discounted = fields.Float(
        compute='_compute_amount_line_no_discount',
        store=True, string='Subtotal')


class AccountInvoice(models.Model):
    """Inherits account.invoice to
    add global discount feature."""

    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal_not_discounted', 'invoice_line_ids.price_subtotal')
    def _compute_amount_all(self):
        amount_untaxed_not_discounted = 0.0
        amount_discounted = 0.0

        for line in self.invoice_line_ids:
            amount_untaxed_not_discounted += \
                line.price_subtotal_not_discounted
            amount_discounted += line.price_subtotal_not_discounted - \
                line.price_subtotal
        self.amount_untaxed_not_discounted = \
            amount_untaxed_not_discounted
        self.amount_discounted = amount_discounted

    amount_discounted = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Discount', store=True)
    amount_untaxed_not_discounted = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Subtotal', store=True)
