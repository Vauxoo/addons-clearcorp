# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class InvoiceLine(models.Model):
    """Inherits account.invoice.line
    and adds discount feature."""

    _inherit = 'account.invoice.line'

    @api.one
    def _compute_price(self):
        super(InvoiceLine, self)._compute_price()
        discount_inv = 1.0 - (self.discount / 100)
        price_subtotal_not_discounted = self.price_subtotal
        if discount_inv != 0.0:
            price_subtotal_not_discounted = price_subtotal_not_discounted / discount_inv
        
        if self.quantity:
            price_unit_not_discounted = price_subtotal_not_discounted / self.quantity
        else:
            price_unit_not_discounted = 0.0
        
        if self.invoice_id and self.invoice_id.currency_id:
            cur = self.invoice_id.currency_id
            price_subtotal_not_discounted = cur.round(price_subtotal_not_discounted)
            price_unit_not_discounted = cur.round(price_unit_not_discounted)
        self.price_subtotal_not_discounted = price_subtotal_not_discounted
        self.price_unit_not_discounted = price_unit_not_discounted

    price_subtotal_not_discounted = fields.Monetary(
        compute='_compute_price',
        currency_field='currency_id', store=True, readonly=True,
        string='Subtotal')
    price_unit_not_discounted = fields.Monetary(
        compute='_compute_price',
        currency_field='currency_id', store=True, readonly=True,
        string='Price unit')


class AccountInvoice(models.Model):
    """Inherits account.invoice to
    add global discount feature."""

    _inherit = 'account.invoice'

    @api.one
    def _compute_amount(self):
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
        super(AccountInvoice, self)._compute_amount()

    amount_discounted = fields.Monetary(
        compute='_compute_amount', currency_field='currency_id',
        string='Discount', store=True, readonly=True)
    amount_untaxed_not_discounted = fields.Monetary(
        compute='_compute_amount', currency_field='currency_id',
        string='Subtotal', store=True, readonly=True)
