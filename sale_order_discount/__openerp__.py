# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Discount',
    'summary': 'Customization from sale.order to apply global discounts',
    'version': '8.0.1.0',
    'category': 'Sales',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    "depends": [
        'sale'
    ],
    'data': [
        'views/sale_order_discount_view.xml'
    ],
}
