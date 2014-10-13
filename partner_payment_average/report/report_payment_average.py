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
from openerp import models, api
from openerp.report import report_sxw

class PaymentAverageReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PaymentAverageReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_partners': self._get_partners,
            'get_invoices_data': self._get_invoices_data,
        })

    def _get_partners(self, partner_ids):
        return self.pool.get('res.partner').browse(self.cr, self.uid, partner_ids)

    def _get_period_ids(self, start_period_id, end_period_id):
        period_obj = self.pool.get('account.period')
        start_period = period_obj.browse(self.cr, self.uid, start_period_id)
        end_period = period_obj.browse(self.cr, self.uid, end_period_id)
        return period_obj.search(self.cr, self.uid,
            [('date_start','>=',start_period.date_start),('date_stop','<=',end_period.date_stop)])

    def _get_invoices_data(self, partner_id, info=None):
        period_ids = self._get_period_ids(info['start_period_id'], info['end_period_id'])
        inv_list = []
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(self.cr, self.uid,
            [('partner_id','=',partner_id),('period_id','in', period_ids)])
        invoices = invoice_obj.browse(self.cr, self.uid, invoice_ids)
        sum = 0
        total_invoices = 0
        for invoice in invoices:
            # Get the last payment that affects average
            payment = invoice.payment_ids.search([], limit=1, order='date desc')
            # If the payment is found add the difference between
            # the invoice date and the payment date to total_days
            if payment and payment.journal_id.affects_avg_customer_payments:
                if payment.date and invoice.date_invoice:
                    total_days = ((datetime.strptime(payment.date,'%Y-%m-%d') - \
                        datetime.strptime(invoice.date_invoice,'%Y-%m-%d')).days) + 1
                    inv_data = {
                        'invoice': {
                            'obj': invoice,
                            'total_days': total_days,
                        },
                        'payment': {
                            'obj': payment,
                        },
                    }
                    sum += total_days
                    total_invoices += 1
                    inv_list.append(inv_data)
        avg = total_invoices and (sum/total_invoices) or 0
        return {
                'elements': inv_list,
                'avg': avg,
                }

class report_payment_average(models.AbstractModel):
    _name = 'report.partner_payment_average.report_payment_average'
    _inherit = 'report.abstract_report'
    _template = 'partner_payment_average.report_payment_average'
    _wrapped_report_class = PaymentAverageReport