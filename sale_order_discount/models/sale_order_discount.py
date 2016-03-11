# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'

    discount = fields.Float('Discount (%)', digits=(16, 2))

    _defaults = {
        'discount': lambda *a: 0.0,
        }

    _sql_constraints = [
        ('check_discount', 'CHECK (discount < 100)',
         'The line discount must be leaser than 100 !'),
    ]


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        super(SaleOrder, self)._amount_all()
        for order in self:
            amount_discount = 0.0
            for line in order.order_line:
                amount_discount += ((line.discount / 100) *
                                    line.price_subtotal)
            amount_total = order.amount_untaxed + order.amount_tax - \
                amount_discount
            order.update({
                'amount_discount': order.currency_id.round(
                    amount_discount),
                'amount_total': order.currency_id.round(amount_total),
            })

    amount_discount = fields.Monetary(compute='_amount_all',
                                      string='Discount', store=True)
