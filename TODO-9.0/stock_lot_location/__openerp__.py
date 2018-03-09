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
    'name': 'Lot Location',
    'version': '1.0',
    'category': 'Warehouse Management',
    'sequence': 17,
    'summary': 'Show Lot Locations',
    'description': """
Add computed lot locations and partners
=======================================
Shows the lot location based on quants location and partners.""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images': [],
    'depends': ['stock'],
    'data': ['stock_lot_location_view.xml'],
    'test': [],
    'demo': [],
    'installable': False,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
