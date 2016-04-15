# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Export Fields',
    'summary': 'Adds a way to edit the export fields lists',
    'version': '9.0.1.0',
    'category': 'Tools',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base'
    ],
    'data': [
        'views/ir_export.xml'
    ],
}
