# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime 
from openerp import models, fields, api, _
from openerp.exceptions import Warning

class Partner(models.Model):

    _inherit = 'res.partner'

    @api.one
    def credit_available_order(self, payment_term, value, date=False):
        # Check param date is available and format date
        if not date:
            date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        else:
            date = date[:10]

        result =  payment_term.compute(value, date_ref=date)[0]
        sum = 0.0
        # elem is a tuple of date, value
        # example ('2014-03-27', 200.65)
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
            date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        else:
            date = date[:10]

        result =  payment_term.compute(value, date_ref=date)[0]
        sum = 0.0
        # elem is a tuple of date, value
        # example ('2014-03-27', 200.65)
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
                if not self.env['res.users'].has_group(
                'account_credit_limit.group_account_exceed_credit_limit'):
                    if not sale_order.partner_id.credit_available_order(sale_order.payment_term,
                    sale_order.amount_total, date=sale_order.date_order)[0]:
                        raise Warning(_('Not enough credit is available to confirm the order.'))
        return super(SaleOrder,self).action_button_confirm()

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.type == 'out_invoice':
                if not self.env['res.users'].has_group(
                'account_credit_limit.group_account_exceed_credit_limit'):
                    if invoice.payment_term:
                        date = invoice.date_invoice or False
                        if not invoice.partner_id.credit_available_invoice(
                        invoice.payment_term, invoice.amount_total, date=date)[0]:
                            raise Warning(_('Not enough credit is available to confirm the invoice.'))
        return super(AccountInvoice,self).invoice_validate()