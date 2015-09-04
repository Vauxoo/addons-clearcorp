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

    price_subtotal = fields.Float(string='Subtotal (discounted)')
    price_subtotal_not_discounted = fields.Float(
        compute='_compute_amount_line_no_discount',
        store=True, string='Subtotal')


class account_invoice_ccorp(models.Model):
    """Inherits account.invoice to
    add global discount feature."""

    _inherit = 'account.invoice'

    @api.multi
    @api.depends('invoice_line.price_subtotal')
    def _compute_amount_all(self):
        for invoice in self:
            amount_untaxed_not_discounted = 0.0
            amount_discounted = 0.0
            invoice_discount = 0.0

            for line in invoice.invoice_line:
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
    amount_untaxed = fields.Float(string='Subtotal (discounted)')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
