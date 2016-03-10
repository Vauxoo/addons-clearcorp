# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    discount = fields.Float('Discount (%)', digits=(16, 2))

    _defaults = {
        'discount': lambda *a: 0.0,
        }

    _sql_constraints = [
        ('check_discount', 'CHECK (discount < 100)',
         'The line discount must be leaser than 100 !'),
    ]


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        super(purchase_order, self)._amount_all()
        for order in self:
            amount_discount = amount_subtotal_discount = 0.0
            for line in order.order_line:
                amount_discount += (100 * line.discount / line.price_subtotal)
            amount_subtotal_discount = order.amount_untaxed - amount_discount
            order.update({
                'amount_discount': order.currency_id.round(amount_discount),
                'amount_subtotal_discount': order.currency_id.round(
                    amount_subtotal_discount),
                'amount_total': amount_subtotal_discount + order.amount_tax,
            })

    amount_total = fields.Monetary(compute='_amount_all',
                                   string='Total', store=True)

    amount_discount = fields.Monetary(compute='_amount_all',
                                      string='Discount', store=True)

    amount_subtotal_discount = fields.Monetary(compute='_amount_all',
                                               string='Subtotal Discount',
                                               store=True)

    @api.cr_uid_id_context
    def action_invoice_create(self, cr, uid, ids, context=None):

        """
        You have to make a super original method and
        update invoice lines with the discount that lines has
        on the purchase order. You can not directly update the discount
        because the discount is calculated on the invoice
        """

        account_invoice_line_obj = self.pool.get('account.invoice.line')

        res = super(purchase_order, self).action_invoice_create(
            cr, uid, ids, context=context)
        invoice_lines_ids = account_invoice_line_obj.search(
            cr, uid, [('invoice_id', '=', res)], context=context)
        invoice_lines = account_invoice_line_obj.browse(
            cr, uid, invoice_lines_ids, context=context)

        for purchase in self.browse(cr, uid, ids, context=context):
            """zip is a function that enables iterating through two
               lists simultaneously.
               for a,b in (list_a,list_b), where a is iterator for list_a
               and b is iterator for list_b
               zip know if any of list is empty and stop the iteration"""

            """In this for, iterates in both list and extract the discount
               for purchase line
               and update the invoice line with the id (invoice_line.id)"""
            for purchase_line, invoice_line in zip(
                    purchase.order_line, invoice_lines):
                if purchase_line.discount is not None:
                    discount = purchase_line.discount
                    account_invoice_line_obj.write(
                        cr, uid, [invoice_line.id], {'discount': discount},
                        context=context)
        return res
