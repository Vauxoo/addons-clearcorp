# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
