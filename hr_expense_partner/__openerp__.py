# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Expense Partner',
    'version': '1.0',
    'author': 'ClearCorp',
    'complexity': 'normal',
    'website': 'http://clearcorp.co.cr',
    'category': 'Human Resources',
    'description': ' Adds partner field to choose supplier for a given expense'
                   ' line, At the account move line creation, sets '
                   ' the chosen partner for that given line instead of '
                   ' the hr_expense supplier',
    'depends': [
        'hr_expense'
    ],
    'init_xml': [],
    'demo_xml': [],
    'data': [
        'views/hr_expense_view.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
}
