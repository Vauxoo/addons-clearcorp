# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Payroll Account Line Partner',
    'version': '1.0',
    'author': 'ClearCorp',
    'summary': ''' Add partners and employees in payroll entries''',
    'category': 'Human Resources',
    'sequence': 10,
    'website': 'http://clearcorp.cr',
    'auto_install': False,
    'application': False,
    'installable': True,
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll_account',
    ],
    'data': [
        'view/hr_payroll_account_line_partner_view.xml',
    ],
}
