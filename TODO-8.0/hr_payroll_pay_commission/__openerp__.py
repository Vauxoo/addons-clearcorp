# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Original Module by SIESA (<http://www.siesacr.com>)
#    Refactored by CLEARCORP S.A. (<http://clearcorp.co.cr>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

{
    'name': 'Pay Commission',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 3,
    'summary': 'Commissions PayRoll',
    'description': """
    # TODO do description
Commissions Rules for Sales
===========================
This module allow Sale Manager to define commission rules based on preset
conditions.

Main Features
-------------
* Commission Percentage
* Post-Expiration Day
* Conditions based on Pricelist, Payment Terms, Amount of Sales, etc.

Note: If you uinstall this module be sure to update the sale_commission module data.""",
    'author': 'CLEARCORP S.A.',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images' : [],
    'depends': [
                'hr_payroll',
                'sale_commission',
                ],
    'data': [
             'view/hr_payroll_pay_commission_view.xml',
             'view/hr_payroll_pay_commission_menu.xml',
             'view/res_config_view.xml',
             'wizard/wizard.xml',
             'report/report.xml',
             'security/ir.model.access.csv',
             ],
    'test' : [],
    'demo': [],
    'installable': False,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}