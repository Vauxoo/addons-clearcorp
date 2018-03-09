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
    'name': 'Point of Sale Remove Line Confirm',
    'version': '1.0',
    'category': 'Point Of Sale',
    'sequence': 7,
    'summary': 'Line remove authorization',
    'description': """
Restrict Line Removal
=====================
* Restricts the users allowed to remove lines.
* Requires authorization to remove a line.""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images' : [],
    'depends': ['point_of_sale'],
    'data': [
             'security/pos_remove_line_confirm_security.xml',
             'views/pos_remove_line_confirm.xml',
             ],
    'test' : [],
    'demo': [],
    'qweb': [
             'static/src/xml/remove_line_confirm.xml',
             ],
    'installable': False,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}