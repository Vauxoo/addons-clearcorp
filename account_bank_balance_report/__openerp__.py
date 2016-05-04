# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Bank Balance Report',
    'version': '8.0.1.2',
    'author': 'ClearCorp',
    'category': 'Finance',
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'summary': """Install the Account Bank Balance Report""",
    'website': "http://clearcorp.cr",
    'depends': ['account_report_lib'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_bank_balance_report_wizard.xml',
        'views/report.xml',
        'viewsreport_menus.xml',
        'views/report_bank_balance.xml'
    ]
}
