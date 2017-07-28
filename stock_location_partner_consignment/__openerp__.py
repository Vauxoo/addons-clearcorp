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
    "name" : 'Consignment stock location on partner',
    "version" : '1.0',
    "author" : 'ClearCorp',
    "summary": "Create a field to set the location for consignment stock on partners.",
    "category": 'Hidden',
    "sequence": 4,
    "depends" : ['stock'],
    "data" : ['res_partner_view.xml'],
    "demo" : [],
    "test" : [],
    "auto_install": False,
    "application": False,
    "installable": True,
    'license': 'AGPL-3',
}