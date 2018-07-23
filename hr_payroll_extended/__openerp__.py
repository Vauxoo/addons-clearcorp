# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Payroll Extended',
    'version': '9.0.1.0',
    'author': 'ClearCorp',
    'website': 'http://clearcorp.cr',
    'category': 'Human Resources',
    'summary': 'Extend functionality to HR Payroll',
    'sequence': 10,
    'license': 'AGPL-3',
    'application': False,
    'installable': False,
    'active': False,
    'depends': [
        'hr_payroll',
        'account',
    ],
    'data': [
        'views/hr_payroll_extended_view.xml',
        'views/hr_payroll_extended_menu.xml',
        'data/hr_payroll_extended_data.xml',
        'security/ir.model.access.csv',
    ],
    'active': False,
    'installable': False,
    'license': 'AGPL-3',
}
