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

from openerp.osv import fields, osv, orm

class OpenInvoicesReportWizard(osv.Model):

    _inherit = "account.report.wiz"
    _name = "open.invoices.wiz"
    _description = "Open Invoices Report Wizard"
    
    _columns = {
       #Redefine filter, use only date and period
       'filter': fields.selection([('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by"),
       'account_type': fields.selection([('customer','Receivable Accounts'),
                                          ('supplier','Payable Accounts'),
                                          ('customer_supplier','Receivable and Payable Accounts')],"Account type",),
       'out_format': fields.selection([('pdf','PDF')], 'Print Format'),
    }
    
    _defaults = {
        'journal_ids':[],
        'out_format': 'pdf',
        'filter': 'filter_date',
        }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        mimetype = self.pool.get('report.mimetypes')
        report_obj = self.pool.get('ir.actions.report.xml')
        context = context or {}
        report_name = 'account_open_invoices_report.report_open_invoices'
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
                'context':context
               }
