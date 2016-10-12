# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Reconcile Filter',
    'summary': 'Change the partner selector in bank reconciliations',
    'version': '9.0.1.0',
    'category': 'Accounting',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,

    'depends': [
        'base',
        'account'
    ],
    'data': [
        "view/account_reconcile_filter.xml",
    ],

}
