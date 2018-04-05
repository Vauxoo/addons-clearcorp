# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base Reporting',
    'summary': 'Base for reporting ',
    'version': '0.9.0001',
    'category': 'Technical Settings',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
    ],
    'data': [
        "views/base_reporting_view.xml",
    ],
}
