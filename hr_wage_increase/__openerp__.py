# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Wage Increase',
    'version': '9.0.1.0',
    'category': 'Human Resources',
    'sequence': 3,
    'summary': 'Contract, Wage, Increase',
    'author': 'ClearCorp',
    'website': 'http://clearcorp.cr',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
    'depends': ['hr_contract'],
    'data': [
        'wizard/increase_wizard_view.xml',
        'views/hr_wage_increase_view.xml',
        'views/hr_wage_increase_menu.xml',
    ],
}
