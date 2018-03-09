# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": 'Personnel Actions',
    "version": '9.0.1.0',
    "author": 'ClearCorp',
    "website": "http://clearcorp.cr",
    "summary": """
        Module to register wage, date, and struct changes in contracts.
    """,
    "category": 'Human Resources',
    "sequence": 4,
    "auto_install": False,
    "application": False,
    "installable": False,
    'license': 'AGPL-3',
    "depends": ['hr_holidays', 'hr_payroll', 'hr_contract'],
    "data": [
              'data/report_paperformat.xml',
              'data/hr_personnel_actions_data.xml',
              'report/report_hr_personnel_actions.xml',
              'report/report_hr_personnel_actions_user.xml',
              'security/ir.model.access.csv',
              'views/hr_personnel_actions_view.xml',
              'views/hr_personnel_actions_menu.xml',
              'views/hr_personnel_actions_report.xml',
    ],
}
