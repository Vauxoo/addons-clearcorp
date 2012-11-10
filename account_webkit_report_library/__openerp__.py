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
    'name': 'Account Webkit Reporting Library',
    'description': """
This a library with methods and templates for easier account reporting using webkit.
It is ment to be used in other modules, it doesn't do anything on its own.
    """,
    'version': '1.0',
    'author': 'CLEARCORP S.A.',
    'category': 'Hidden',
    'website': "http://clearcorp.co.cr",
    'images': [],
    'depends': ['account','report_webkit'],
    'init_xml': [],
    'demo_xml' : [],
    'update_xml': [
        'res_company_view.xml',
        'webkit_headers/webkit_headers.xml',
    ],
    'test': [],
    'active': False,
    'installable': True,
    'license': 'AGPL-3',
}
