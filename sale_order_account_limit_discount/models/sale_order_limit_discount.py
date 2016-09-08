# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from openerp.exceptions import UserError
from openerp.tools.translate import _


class SaleOrderLine(models.Model):
    """Changes the confirm button to check if the user has the necessary
    permissions to modify an item's price and/or discount."""

    _inherit = 'sale.order.line'
    # Discount percentage, per sale.py
    _lower_tier_discount = 10
    _higher_tier_discount = 20

    @api.multi
    @api.constrains('price_unit')
    def _check_price_and_discount(self):
        # Checks the groups to which a user may belong and assigns a cap to
        # the discount they can give.

        # Current user
        current_user = self.env['res.users'].browse(self.env.uid)

        unlimited_group = False

        # No limit discount group.
        if current_user.has_group(
                'sale_order_account_limit_discount.group_no_limit_discount'):
            max_discount = 100
            unlimited_group = True
        # High-tier discount group.
        elif current_user.has_group(
                'sale_order_account_limit_discount.group_higher_limit_discount'
        ):
            max_discount = self._higher_tier_discount
        # Lower discount group.
        else:
            max_discount = self._lower_tier_discount

        # Checks the sale order lines to limit.
        # Checks that the discount is not over the allowed percentage
        # related to the user's group.
        if self.discount > max_discount:
            raise UserError(_('The discount for %s exceeds the '
                              'company\'s discount limits.')
                            % self.name)

        # Checks that the price hasn't changed relative to the price
        # list if the user doesn't belong to the unlimited
        # discount group.
        if not unlimited_group:
            # This brings back the product's original attributes.
            # It needs a pricelist and partner_id to suceed.
            if self.order_id.pricelist_id and \
                    self.order_id.partner_id:
                # Gets the product's current price, according to context.
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
                if self.price_unit != product.price:
                    raise UserError(_('You are not allowed to '
                                      'change the price of %s.')
                                    % self.name)
            else:
                raise UserError(_('One of the items for %s '
                                  'doesn\'t have a pricelist or '
                                  'an associated partner.')
                                % self.name)
