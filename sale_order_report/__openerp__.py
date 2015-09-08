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
    "name": 'Sale Order report',
    "version": '2.0',
    "author": 'ClearCorp',
    'complexity': 'normal',
    "description": """
Sale order report in Qweb
    """,
    "category": 'Sales',
    "sequence": 4,
    "website": "http://clearcorp.co.cr",
    "images": [],
    "depends": [
        'sale_order_discount',
        'sale_order_extended',
        'account_report_lib',
        'website_quote',
        ],
    "init_xml": [],
    "demo_xml": [],
    "data": [
                'data/report.paperformat.xml',
                'data/sale_report.xml',
                'views/report_sale_order.xml',
                'views/report_sale_order_layout.xml',
                'views/report_sale_order_layout_header.xml',
                'views/report_sale_order_layout_footer.xml',
                ],
    "test": [],
    "auto_install": False,
    "application": False,
    "installable": True,
    'license': 'AGPL-3',
}
