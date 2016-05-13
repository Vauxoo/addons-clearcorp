# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Payroll MultiCurrency',
    'summary': 'Add multicurrency to payroll',
    'version': '8.0.1.0',
    'category': 'HR',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'hr_payroll',
    ],
    'data': [
        "views/hr_payroll_multicurrency_view.xml",
    ],
}
