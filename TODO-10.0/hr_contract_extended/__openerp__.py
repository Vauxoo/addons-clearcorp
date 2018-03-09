# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Contract Extended',
    'version': '9.0.1.0',
    'author': 'ClearCorp',
    'website': 'http://clearcorp.cr',
    'category': 'Human Resources',
    'summary': 'Extend functionality to HR Contract',
    'sequence': 10,
    'license': 'AGPL-3',
    'application': False,
    'installable': False,
    'active': False,
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'views/hr_contract_extended_view.xml',
        'security/hr_contract_extended_security.xml',
        'security/ir.model.access.csv',
                ],

}
