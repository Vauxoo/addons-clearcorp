# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Voucher Report',
    'summary': 'Voucher Report',
    'version': '8.0.1.0',
    'category': 'Uncategorized',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'account_voucher',
    ],
    'data': [
        'data/report_paperformat.xml',
        "views/report_account_voucher.xml",
        "views/account_voucher_report.xml",
    ],
}
