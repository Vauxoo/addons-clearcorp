# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Company prefix',
    'summary': 'Add prefix in company',
    'version': '1.0',
    'category': 'Hidden',
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
        'views/base_company_prefix.xml'
    ],
}
