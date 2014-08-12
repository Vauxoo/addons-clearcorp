# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Hr Payroll Report',
    'version': '1.0',
    "author" : 'CLEARCORP S.A.',
    'website': 'http://clearcorp.co.cr',
    'category': 'Human Resources',
    'description': """
Hr Payroll Report
===================
This module modifies these reports:
    * Payroll Report
    * Report Employee by Periods
    * Report Employee by Month
    * Payslip Details 
    * Payslip
    
Also, modifies:
    * Employee Contracts
    * Fortnightly Payroll Register
    """,
    'depends': [
        'account',
        'report_webkit_lib',
        'hr_payroll_account',
        'hr_payroll_extended',
    ],
    'data': [
             'security/ir.model.access.csv',
             'report/report.xml',
             'wizard/hr_payroll_report_for_month_wizard_view.xml',
             'wizard/hr_payroll_report_employee_by_periods_wizard_view.xml',
             'hr_payroll_report_view.xml',
             'report_menus.xml',
            ],
    'active': False,
    'installable': True,    
    'license': 'AGPL-3',
}
