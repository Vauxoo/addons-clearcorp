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
    'name': 'Sale Commission',
    'version': '1.0',
    'category': 'Sales Management',
    'sequence': 3,
    'summary': 'Commissions over Sales',
    'description': """
Commissions Rules for Sales
===========================
This module allow Sale Manager to define commission rules based on preset
conditions.

Main Features
-------------
* Commission Percentage
* Post-Expiration Day
* Conditions based on Pricelist, Payment Terms, Amount of Sales, etc.
""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images': [],
    'depends': [
                'sale',
                'account_invoice_discount',
                ],
    'data': [
             'data/report_paperformat.xml',
             'security/sale_commission_security.xml',
             'security/ir.model.access.csv',
             'sale_commission_view.xml',
             'sale_commission_menu.xml',
             'views/report_sale_commission.xml',
             'sale_commission_report.xml',
             'wizard/wizard.xml',
             ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
