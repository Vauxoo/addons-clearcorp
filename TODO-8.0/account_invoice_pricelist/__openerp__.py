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
    'name': 'Invoice Pricelist',
    'version': '1.0',
    'category': 'Purchase Management',
    'sequence': 3,
    'summary': 'Invoices Pricelist from Sale Orders and Purchase Orders',
    'description': """
Add Invoice Pricelist
=====================

This module adds and links the Sale and Purchase Orders Pricelist with the Invoice.""",
    'author': 'CLEARCORP S.A.',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'easy',
    'images' : [],
    'depends': ['account','purchase','sale_stock'],
    'data': [
             'view/account_invoice_pricelist_view.xml',
             ],
    'test' : [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}