# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner Routes',
    'summary': 'This is a module about of partner routes',
    'version': '9.0.1.0',
    'category': 'Sale',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,

    'depends': [
        'stock',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'partner_routes_menu.xml',
        'views/stock_picking_view.xml',
        'views/report_res_partner_route.xml',
    ],

}
