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
    'name' : 'Account Invoice Limit Discount',
    'author' : 'CLEARCORP S.A.',
    'description': """
Account Invoice Limit Discount.
================================
Configuration:
---------------
For set the maximum discount for each company:
Settings -> Accounting -> Accounting -> Maximum Discount

This module adds a security group. The users that are not in this group
can not add, in each invoice line, a discount greater that the allowed in
the company.
""",
    'version' : '1.0',
    'category': 'Accounting & Finance',
    'website' : 'http://clearcorp.co.cr',
    'depends' : ['base','account',],
    'data' : [
              'security/account_invoice_limit_discount.xml',
              'account_config_settings_inherit.xml'
              ],
    'test': [],
    'active': False,
    'installable': True,
    'license': 'AGPL-3',
}