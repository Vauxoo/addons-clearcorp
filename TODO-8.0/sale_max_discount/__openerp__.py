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
    'name' : 'Sales Max Discount',
    'author' : 'ClearCorp',
    'description': """
Limit the discount amount allowed in Sale Orders and Invoices""",
    'version' : '1.0',
    'category': 'Sales Management',
    'website' : 'http://clearcorp.co.cr',
    'depends' : [
                 'sale',
                 'account',
                 ],
    'data' : [
              'views/sale_max_discount_view.xml',
              'views/sale_config_settings_view.xml',
              'security/sale_max_discount_security.xml',
              ],
    'test': [],
    'active': False,
    'installable': False,
    'license': 'AGPL-3',
}