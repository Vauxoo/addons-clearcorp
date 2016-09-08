# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
from openerp.exceptions import UserError
from openerp.tools.translate import _


class AccountInvoice(models.Model):
    """Changes the account.invoice.basic workflow to check if the user has
    the necessary permissions to modify an item's price and/or discount."""

    _inherit = 'account.invoice'
    # Discount percentages, according to each group.
    _lower_tier_discount = 10
    _higher_tier_discount = 20

    @api.model
    def invoice_validate(self):
        # Current user
        current_user = self.env['res.users'].browse(self.env.uid)

        # Checks the groups to which a user may belong.
        # No limit discount group.
        if current_user.has_group(
                'sale_limit_discount.group_no_limit_discount'):
            max_discount = 100
        # High-tier discount group
        elif current_user.has_group(
                'sale_limit_discount.group_higher_limit_discount'
        ):
            max_discount = self._higher_tier_discount
        # Lower discount group
        else:
            max_discount = self._lower_tier_discount

        # Checks the invoice lines to limit
        for line in self.invoice_line_ids:
            if line.discount > max_discount:
                raise UserError(_('The discount for %s exceeds the '
                                  'company\'s discount limits.')
                                % line.name)

        return super(AccountInvoice, self).invoice_validate()
