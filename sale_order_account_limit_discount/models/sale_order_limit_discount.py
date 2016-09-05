# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, osv
from openerp.tools.translate import _


class SaleOrder(models.Model):
    """Changes the confirm button to check if the user has the necessary
    permissions to modify an item's price and/or discount."""

    _inherit = 'sale.order'
    # Discount percentage, per sale.py
    _lower_tier_discount = 10
    _higher_tier_discount = 20

    @api.model
    def action_button_confirm(self):
        # Checks the groups to which a user may belong and assigns a cap to
        # the discount they can give.

        unlimited_group = False
        # No limit discount group.
        if self.env['res.users'].has_group(
                'sale_order_limit_discount.group_no_limit_discount'):
            max_discount = 100
            unlimited_group = True
        # High-tier discount group.
        elif self.env['res.users'].has_group(
                'sale_order_limit_discount.group_higher_limit_discount'):
            max_discount = self._higher_tier_discount
        # Lower discount group.
        else:
            max_discount = self._lower_tier_discount

        # Checks the sale orders to limit.
        for sale_order in self.browse():
            for line in sale_order.order_line:
                # Checks that the discount is not over the allowed percentage
                # related to the user's group.
                if line.discount > max_discount:
                    raise osv.except_osv(_('Discount Error'),
                                         _('The discount for %s exceeds the '
                                           'company\'s discount limits.')
                                         % line.name)

                # Checks that the price hasn't changed related to the price
                # list if the user doesn't belong to the unlimited
                # discount group.
                if not unlimited_group:
                    # This brings back the product's original attributes.
                    # It needs a pricelist and partner_id to suceed.
                    if line.order_id.pricelist_id and \
                            line.order_id.partner_id:
                        product = self.product_id.with_context(
                            lang=self.order_id.partner_id.lang,
                            partner=self.order_id.partner_id.id,
                            quantity=self.product_uom_qty,
                            date_order=self.order_id.date_order,
                            pricelist=self.order_id.pricelist_id.id,
                            uom=self.product_uom.id,
                            fiscal_position=self.env.context.get(
                                'fiscal_position')
                        )
                        if line.price_unit != product.price:
                            raise osv.except_osv(_('Price Error'),
                                                 _('You are not allowed to '
                                                   'change the price of'
                                                   '%s.')
                                                 % line.name)

                    else:
                        raise osv.except_osv(_('Price Error'),
                                             _('One of the items '
                                               'for %s doesn\'t '
                                               'have a pricelist or '
                                               'an associated partner.')
                                             % line.name)

        return super(SaleOrder, self).action_confirm()
