# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'QWeb xlsx Reports',
    'summary': 'Create xlsx reports using QWeb templates',
    'version': '9.0.1.0',
    'category': 'Base',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 16,
    'application': False,
    'installable': False,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'xlsxwriter'
        ],
    },
    'depends': [
        'report'
    ],
    'data': [
        'report_xls_view.xml',
        'views/assets.xml',
    ],
}
