# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase Order Discount',
    'summary': 'This module add discount to purchase order object',
    'version': '9.0.1.0',
    'category': 'Purchase Management',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'purchase',
        'account_invoice_discount',
    ],
    'data': [
        'views/purchase_order_discount_view.xml',
    ],
}
