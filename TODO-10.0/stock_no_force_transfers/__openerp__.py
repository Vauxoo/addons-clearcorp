# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Inventory No Force',
    'summary': 'Allow to no Forcer Inventory Transferences',
    'version': '9.0.1.0',
    'category': 'Technical Settings',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,

    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/stock_no_force_transfer_security.xml',
        'views/stock_piking_no_transfer_view.xml',
    ],

}
