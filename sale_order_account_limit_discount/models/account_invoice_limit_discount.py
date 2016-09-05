# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, osv
from openerp.tools.translate import _


class AccountInvoice(models.Model):
    """Changes the account.invoice.basic workflow to check if the user has
    the necessary permissions to modify an item's price and/or discount."""

    _inherit = 'account.invoice'
    # Discount percentage, per account_invoice.py
    _lower_tier_discount = 10
    _higher_tier_discount = 20

    @api.model
    def invoice_validate(self):
        unlimited_group = False
        # Checks the groups to which a user may belong.
        # No limit discount group.
        if self.env['res.users'].has_group(
                'sale_order_limit_discount.group_no_limit_discount'):
            max_discount = 100
            unlimited_group = True
        # High-tier discount group
        elif self.env['res.users'].has_group(
                'sale_order_limit_discount.group_higher_limit_discount'):
            max_discount = self._higher_tier_discount
        # Lower discount group
        else:
            max_discount = self._lower_tier_discount

        # Checks the sale orders to limit
        for account_invoice in self.browse():
            for line in account_invoice.invoice_line_ids:
                if line.discount > max_discount:
                    raise osv.except_osv(_('Discount Error'),
                                         _('The discount for %s exceeds the '
                                           'company\'s discount limits.')
                                         % line.name)
                #if not unlimited_group:
                #    if line.price_unit

        return super(AccountInvoice, self).invoice_validate()
