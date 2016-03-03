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

from openerp import models, fields, api
from datetime import timedelta, datetime

class Partner(models.Model):

    _inherit = 'res.partner'

    @api.one
    def _compute_average_payment(self):
        # Get all paid invoices
        invoice_obj = self.env['account.invoice']
        invoices = invoice_obj.search(
            [('partner_id','=',self.id),('state','=','paid')])
        total_days = 0
        total_invoices = 0
        for invoice in invoices:
            # Get the last payment that affects average
            payment = invoice.payment_ids.search([('id','in',invoice.payment_ids.ids)], limit=1, order='date desc')
            # If the payment is found add the difference between
            # the invoice date and the payment date to total_days
            if payment and payment.journal_id.affects_avg_customer_payments:
                total_days += ((datetime.strptime(payment.date,'%Y-%m-%d') - \
                    datetime.strptime(invoice.date_invoice,'%Y-%m-%d')).days) + 1
                total_invoices += 1
        # Check if any invoice was computed
        if total_invoices:
            self.average_payment_days = total_days / total_invoices
        else:
            self.average_payment_days = 0

    average_payment_days = fields.Integer(string='Average Payment Days',
        compute='_compute_average_payment',
        help='Average number of days elapsed until the invoice payment.')