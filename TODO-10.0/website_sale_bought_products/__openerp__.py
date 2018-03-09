# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Auto-Suggested Products',
    'summary': 'Generate a suggested products list based on last buyers',
    'version': '9.0.1.0',
    'category': 'Website',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'depends': [
        'website_sale'
    ],
    'data': [
        'views/settings_suggest_product_view.xml',
        'views/suggest_products_view.xml'
    ],
}
