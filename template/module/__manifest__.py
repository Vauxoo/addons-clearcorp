# -*- coding: utf-8 -*-
# © <YEAR(S)> ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Module name',
    'summary': 'Module summary',
    'version': '9.0.1.0',
    'category': 'Uncategorized',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
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
        'base',
    ],
    'data': [
        'security/module_name_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/report_name.xml',
        'views/model_name_view.xml',
        'wizards/wizard_model_view.xml',
    ],
    'demo': [
        'demo/module_name_demo.xml',
    ],
    'qweb': [
        'static/src/xml/module_name.xml',
    ],
}
