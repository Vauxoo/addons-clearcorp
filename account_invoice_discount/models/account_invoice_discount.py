# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class InvoiceLine(models.Model):
    """Inherits account.invoice.line
    and adds discount feature."""

    _inherit = 'account.invoice.line'

    @api.multi
    @api.depends('price_unit', 'quantity')
    def _compute_amount_line_no_discount(self):
        for line in self:
            if line.invoice_id and line.invoice_id.currency_id:
                cur = line.invoice_id.currency_id
                line.price_subtotal_not_discounted = cur.round(
                    line.price_unit * line.quantity)
            else:
                line.price_subtotal_not_discounted = \
                    line.price_unit * line.quantity

    price_subtotal_not_discounted = fields.Float(
        compute='_compute_amount_line_no_discount',
        store=True, string='Subtotal')


class account_invoice(models.Model):
    """Inherits account.invoice to
    add global discount feature."""

    _inherit = 'account.invoice'

    @api.multi
    @api.depends('invoice_line_ids.price_subtotal')
    def _compute_amount_all(self):
        for invoice in self:
            amount_untaxed_not_discounted = 0.0
            amount_discounted = 0.0
            invoice_discount = 0.0

            for line in invoice.invoice_line_ids:
                amount_untaxed_not_discounted += \
                    line.price_subtotal_not_discounted
                amount_discounted += line.price_subtotal_not_discounted - \
                    line.price_subtotal
            if amount_untaxed_not_discounted:
                invoice_discount = 100 * amount_discounted / \
                    amount_untaxed_not_discounted
            invoice.amount_untaxed_not_discounted = \
                amount_untaxed_not_discounted
            invoice.amount_discounted = amount_discounted
            invoice.invoice_discount = invoice_discount

    invoice_discount = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Discount (%)', store=True)
    amount_discounted = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Discount', store=True)
    amount_untaxed_not_discounted = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Subtotal', store=True)
