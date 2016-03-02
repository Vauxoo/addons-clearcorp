# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Job',
    'summary': 'Active or inactive the job profile in HR',
    'version': '8.0.1.0',
    'category': 'Human Resources',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'hr',
    ],
    'data': [
        "views/hr_job_view.xml",
    ],
}
