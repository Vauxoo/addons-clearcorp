# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Calendar Clear All',
    'summary': 'Clear all selected calendar summary',
    'version': '9.0.1.0',
    'category': 'Extra Tools',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 135,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'calendar',
    ],
    'data': [
        'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/calendar_clear_all.xml'
    ],
}
