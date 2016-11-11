# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Credit Limit',
    'version': '1.0',
    'author': 'ClearCorp',
    'complexity': 'easy',
    'description': '''
Partner Credit Validation
=========================
Check and verify the total credit amount when validating Sale Orders and
Customer Invoices.

Main Features
-------------
* Unlimited Payment group to allow users exceed the credit limit
* Validation of Partner total credit on Sale Orders and Customer Invoices
''',
    'category': 'Accounting & Finance',
    'sequence': 15,
    'website': 'http://clearcorp.co.cr',
    'images': [],
    'depends': [
        'base',
        'account',
        'sale'
    ],
    'data': [
        'security/account_credit_limit_security.xml',
    ],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [],
    'test': [],
    'auto_install': False,
    'application': False,
    'installable': True,
    'license': 'AGPL-3',
}
