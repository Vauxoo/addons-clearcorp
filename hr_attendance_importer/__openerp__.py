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
    'name' : 'Attendance Importer',
    'version' : '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'easy',
    'description': '''
Import employee attendances from cvs files
==========================================
This module allows you to import employee attendances from a cvs standard file
using a wizard that allows you to correct and verify any invalid item.

Main features:
--------------
* Item validation
* Date format definition
* Unique employee code
* Normal and extra hours identification
''',
    'category': 'Human Resources',
    'sequence': 3,
    'website' : 'http://clearcorp.co.cr',
    'images' : [],
    'depends' : [
                 'hr_attendance',
                 ],
    'data' : [
              'view/hr_attendance_importer_view.xml',
              'view/hr_attendance_importer_menu.xml',
              'view/res_config_view.xml',
              'wizard/wizard_view.xml',
              'data/hr_attendance_importer_data.xml',
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