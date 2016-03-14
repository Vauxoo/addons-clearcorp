# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class InvoiceLine(models.Model):
    """Inherits account.invoice.line
    and adds discount feature."""

    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('price_unit', 'product_uom_qty')
    def _compute_amount_line_no_discount(self):
        for line in self:
            if line.order_id and line.order_id.currency_id:
                cur = line.order_id.currency_id
                line.price_subtotal_not_discounted = cur.round(
                    line.price_unit * line.product_uom_qty)
            else:
                line.price_subtotal_not_discounted = \
                    line.price_unit * line.product_uom_qty

    price_subtotal_not_discounted = fields.Float(
        compute='_compute_amount_line_no_discount',
        store=True, string='Subtotal')


class SaleOrder(models.Model):
    """Inherits account.invoice to
    add global discount feature."""

    _inherit = 'sale.order'

    @api.multi
    @api.depends('order_line.price_subtotal_not_discounted')
    def _compute_amount_all(self):
        for order in self:
            amount_untaxed_not_discounted = 0.0
            amount_discounted = 0.0
            order_discount = 0.0

            for line in order.order_line:
                amount_untaxed_not_discounted += \
                    line.price_subtotal_not_discounted
                amount_discounted += line.price_subtotal_not_discounted - \
                    line.price_subtotal
            if amount_untaxed_not_discounted:
                order_discount = 100 * amount_discounted / \
                    amount_untaxed_not_discounted
            order.amount_untaxed_not_discounted = \
                amount_untaxed_not_discounted
            order.amount_discounted = amount_discounted
            order.order_discount = order_discount

    order_discount = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Discount (%)')
    amount_discounted = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Discount', store=True)
    amount_untaxed_not_discounted = fields.Float(
        compute='_compute_amount_all',
        digits=dp.get_precision('Account'),
        string='Subtotal', store=True)
