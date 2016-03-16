# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Res Partner Slow Payer',
    'summary': 'Add the field slow_payer in the partner',
    'version': '8.0.1.0',
    'category': 'Extra Tools',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'account',
        'sale',
    ],
    'data': [
        "views/res_partner_slow_payer_view.xml",
    ],
}
