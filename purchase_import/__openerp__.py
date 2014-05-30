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
    'name': 'Purchase Import',
    'version': '1.0',
    'category': 'Purchase Management',
    'sequence': 20,
    'summary': 'Import Purchase, Tax Charges, And Cost Calculation',
    'description': """
Manage Taxes on Import Purchases
================================

Purchase Import facilitates the handling of Imports, adding tax charges and calculates the total product's cost""",
    'author': 'CLEARCORP S.A.',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images' : [],
    'depends': ['purchase','res_currency_sequence', 'stock','mail', 'report_aeroo_ooo'],
    'data': [
             'view/purchase_import_view.xml',
             'view/purchase_import_menu.xml',
             'purchase_import_sequence.xml',
             'purchase_import_workflow.xml',
             'data/purchase_import_data.xml',
             'report/purchase_import_report.xml',
             'security/ir.model.access.csv',
             ],
    'test' : [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}