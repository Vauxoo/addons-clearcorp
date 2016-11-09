# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Partner Trade Name',
    'summary': 'This module add field trade name to partners',
    'version': '9.0.1.0',
    'category': 'Extra Tools',
    'website': "http://clearcorp.cr",
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
    ],
    'data': [
        'views/partner_trade_name.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
}
