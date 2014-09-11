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
    'name' : 'Attendance Payslip',
    'version' : '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'normal',
    'description': '''
Calculate Workdays From the user attendance
===========================================
This module allows you to use the attendances as reference to compute and calculate the 
working hours for employees.

Main features:
--------------
* Contract selection for attendance computation
* HN code for normal hours
* EH code for extra hours

Warning: Does not support multiple contracts per user
''',
    'category': 'Human Resources',
    'sequence': 3,
    'website' : 'http://clearcorp.co.cr',
    'images' : [],
    'depends' : [
                 'hr_payroll',
                 'hr_attendance',
                 ],
    'data' : [
              'view/hr_attendance_payslip_view.xml',
              ],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [],
    'test' : [],
    'auto_install': False,
    'application': False,
    'installable': True,
    'license': 'AGPL-3',
}