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
    'name': 'Wage Increase',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 3,
    'summary': 'Contract, Wage, Increase',
    'description': """
Increase the contract wage
==========================

This module allow you to increase the employees wage using a simple wizard.

Main features
-------------

* Multiple contract selection
* Increase by fixed amount
* Percent increase
""",
    'author': 'CLEARCORP S.A.',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'easy',
    'images' : [],
    'depends': ['hr_contract',],
    'data': [
             'wizard/increase_wizard_view.xml',
             'view/hr_wage_increase_view.xml',
             'view/hr_wage_increase_menu.xml',
             ],
    'test' : [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}