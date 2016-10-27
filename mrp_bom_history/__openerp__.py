# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'MRP Bill of Materials History',
    'summary': 'Historic of bill of materials modifications',
    'version': '8.0.1.0',
    'category': 'Manufacturing',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 19,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_history_view.xml',
    ],
}
