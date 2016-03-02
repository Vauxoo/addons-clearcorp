# -*- coding: utf-8 -*-
# © <YEAR(S)> ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Incoterm',
    'summary': 'Add incoterm to invoice',
    'version': '8.0.1.0',
    'category': 'Accounting & Finance',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'sale',
        'stock_account',
    ],
    'data': [
        "views/account_invoice_incoterm_view.xml",
    ],
}
