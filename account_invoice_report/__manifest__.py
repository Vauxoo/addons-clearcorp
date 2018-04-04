# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice Report',
    'summary': 'Invoice webkit report',
    'version': '0.9.0001',
    'category': 'Accounting & Finance',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'base',
        'account_invoice_discount',
        'base_reporting',
        ],
    'data': [
        'data/report.paperformat.xml',
        'data/invoice_report.xml',
        'views/res_company_view.xml',
        'views/report_invoice_layout.xml',
        'views/report_invoice_layout_header.xml',
        'views/report_invoice_layout_footer.xml',
        'views/report_account_invoice.xml',
    ],
}
