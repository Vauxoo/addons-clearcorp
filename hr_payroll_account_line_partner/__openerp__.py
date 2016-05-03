# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Payroll Account Line Partner',
    'version': '9.0.1.0.2',
    'author': 'ClearCorp',
    'summary': ''' Add partners and employees in payroll entries''',
    'category': 'Human Resources',
    'website': 'http://clearcorp.cr',
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll_account',
    ],
    'data': [
        'view/hr_payroll_account_line_partner_view.xml',
    ],
}
