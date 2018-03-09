# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Payment Report',
    'summary': 'This module allows the user to create a '
               'half-page report for invoices.',
    'version': '9.0.1.0',
    'category': 'Accounting & Finance',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 31,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'account',
        'l10n_cr_amount_to_text'
    ],
    'data': [
        'data/report_paperformat.xml',
        'views/account_payment_report_header.xml',
        'views/account_payment_report_footer.xml',
        'views/account_payment_report.xml',
        'views/report_account_payment.xml'
    ]
}
