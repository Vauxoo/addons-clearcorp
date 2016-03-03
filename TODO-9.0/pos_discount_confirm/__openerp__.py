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
    'name': 'Point of Sale Discount Confirm',
    'version': '1.0',
    'category': 'Point Of Sale',
    'sequence': 7,
    'summary': 'Required authorized users to apply discounts',
    'description': """
Restrict Discounts
==================
* Restricts the users allowed to apply and modify discounts.
* Requires authorization to apply a discount.""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images' : [],
    'depends': ['point_of_sale'],
    'data': [
             'security/pos_discount_confirm_security.xml',
             'views/pos_discount_confirm.xml',
             ],
    'test' : [],
    'demo': [],
    'qweb': [
             'static/src/xml/discount_confirm.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
