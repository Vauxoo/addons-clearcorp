# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv


class OpenInvoicesReportWizard(osv.TransientModel):

    _inherit = "account.report.wiz"
    _name = "open.invoices.wiz"
    _description = "Open Invoices Report Wizard"
    
    _columns = {
       # Redefine filter, use only date and period
       'filter': fields.selection(
           [('filter_date', 'Date'), ('filter_period', 'Periods')],
           "Filter by"),
       'account_type': fields.selection(
           [('customer', 'Receivable Accounts'),
            ('supplier', 'Payable Accounts'),
            ('customer_supplier', 'Receivable and Payable Accounts')],
           "Account type",),
       'out_format': fields.selection(
           [('pdf', 'PDF'), ('xls', 'XLS')], 'Print Format'),
    }
    
    _defaults = {
        'journal_ids': [],
        'out_format': 'pdf',
        'filter': 'filter_date',
        }
    
    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        if wizard.out_format == 'pdf':
            res = self.pool.get('report').get_action(
                cr, uid, ids,
                'account_open_invoices_report.report_open_invoices',
                data=data, context=context)

        elif wizard.out_format == 'xls':
            res = self.pool.get('report').get_action(
                cr, uid, ids,
                'account_open_invoices_report.report_open_invoices_xls',
                data=data, context=context)
        return res
