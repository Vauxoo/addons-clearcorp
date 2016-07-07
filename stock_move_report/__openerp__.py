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
    'name': 'Stock Move Report',
    'version': '1.0',
    "author": 'ClearCorp',
    'category': 'Warehouse Management',
    'description': """
Stock Move Report
====================
This module add stock move report
""",
    'website': 'http://clearcorp.co.cr',
    'depends': [
                'stock', 'product', 'report_xls_template'
        ],
    'data': ['security/ir.model.access.csv',
             'stock_move_report_report.xml',
             'report_stock_move_order.xml',
             'views/report_stock_move_pdf.xml',
             'views/report_picking.xml',
             'report/stock_move_analysis.xml',
             'views/report_stock_move_xls.xml',
             'views/report_stock_move_order.xml',
             'views/view_company_form.xml',
             'wizard/stock_move_report_wizard.xml',
             'wizard/stock_move_order_wizard.xml'
             ],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
}
