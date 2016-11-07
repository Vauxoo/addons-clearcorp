# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Order Terms & Conditions',
    'version': '1.0',
    'category': 'sales',
    'sequence': 20,
    'summary': '',
    'description': """
Add Terms & Conditions to the sale order
========================================
""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images': [],
    'depends': [
        'base',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_terms_and_conds_view.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
