# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Open Invoices Report',
    'version': '1.0',
    'author': 'ClearCorp',
    'category': 'Accounting & Finance',
    'description': """
Open Invoice Report.
==============================
This module modifies the open invoice report """,
    'website': 'http://clearcorp.co.cr',
    'depends': [
        'account',
        'account_voucher',
        'account_report_lib',
        'report_xls_template',
    ],
    'data': [
        'wizard/account_open_invoices_report_wizard_view.xml',
        'report/report.xml',
        'report_menus.xml',
        'views/report_open_invoices.xml',
        'views/report_open_invoices_xls.xml',
    ],
    'active': False,
    'installable': True,    
    'license': 'AGPL-3',
}
