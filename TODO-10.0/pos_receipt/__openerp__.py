# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Point of Sale Receipt',
    'version': '9.0.1.0',
    'category': 'Point Of Sale',
    'sequence': 7,
    'summary': 'Standard Receipt',
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'depends': [
        'point_of_sale'
    ],
    'data': [
        'views/pos_receipt.xml'
    ],
    'qweb': [
        'static/src/xml/pos_receipt.xml'
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
