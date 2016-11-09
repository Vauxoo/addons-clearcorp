# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import models, api, _
from openerp.exceptions import Warning


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def credit_available_order(self, payment_term, value, date=False):
        # Check param date is available and format date
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            date = date[:10]
        result = payment_term.compute(value, date_ref=date)[0]
        sum = 0.0
        # elem is a tuple of date, value
        # example ('2016-11-11', 200.65)
        for elem in result:
            if elem[0] != date:
                sum += elem[1]

        if sum == 0.0:
            return True
        else:
            if self.credit + sum <= self.credit_limit:
                return True
            else:
                return False

    @api.one
    def credit_available_invoice(self, payment_term, value, date=False):
        # Check param date is available
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            date = date[:10]

        result = payment_term.compute(value, date_ref=date)[0]
        sum = 0.0
        # elem is a tuple of date, value
        # example ('2016-11-11', 200.65)
        for elem in result:
            if elem[0] != date:
                sum += elem[1]

        if sum == 0.0:
            return True
        else:
            if self.credit - sum <= self.credit_limit:
                return True
            else:
                return False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for sale_order in self:
            if sale_order.payment_term:
                if not self.env['res.users']. \
                        has_group('account_credit_limit.'
                                  'group_account_exceed_credit_limit'):
                    if not sale_order.partner_id. \
                            credit_available_order(sale_order.payment_term,
                                                   sale_order.amount_total,
                                                   date=
                                                   sale_order.date_order)[0]:
                        raise Warning(_('Not enough credit is available to '
                                        'confirm the order.'))
        return super(SaleOrder, self).action_button_confirm()


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.type == 'out_invoice':
                if not self.env['res.users'].has_group(
                        'account_credit_limit.'
                        'group_account_exceed_credit_limit'):
                    if invoice.payment_term:
                        date = invoice.date_invoice or False
                        if not invoice.partner_id.credit_available_invoice(
                                invoice.payment_term, invoice.amount_total,
                                date=date)[0]:
                            raise Warning(_(
                                'Not enough credit is available '
                                'to confirm the invoice.'))
        return super(AccountInvoice, self).invoice_validate()
