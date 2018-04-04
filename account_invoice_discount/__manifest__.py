# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Invoice discount',
    'summary': 'Adds a discount feature for invoice',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'website': "http://clearcorp.cr",
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 4,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': ['account'],
    'data': [
        'views/account_invoice_discount_view.xml',
    ],
}
