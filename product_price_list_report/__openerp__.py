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
    'name': 'Product Pricelist Report',
    'description': """ 
Product Report
=================
This module pass pricelist report (it was in rml) to a aeroo report template. In
case that product has image, report will print this image.
    """,
    'version': '1.0',
    'author': 'CLEARCORP S.A.',
    'category': 'Sales Management',
    'website': "http://clearcorp.co.cr",
    'depends': ['product','account_report_lib'],
    'data': ['report/report.xml'],
    'active': False,
    'installable': True,
    'license': 'AGPL-3',
}
