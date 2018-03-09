# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Restrict Export',
    'summary': 'Restrict export option in all menus.',
    'version': '9.0.1.0',
    'category': 'Technical Settings',
    'website': 'http://clearcorp.cr',
    'author': 'Khwunchai Jaengsawang, ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': False,
    'auto_install': False,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },

    'depends': [
        'web'
    ],

    'data': [
        'security/security.xml',
        'views/webclient_templates.xml',
    ],
}
