#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name' : 'Account Invoice Move Discount',
    'version' : '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'normal',
    'description': '''
Customer Invoice and Customer Refund discount 
=============================================
Creates Journal Items for discounts in Customer invoices and refunds
''',
    'category': 'Accounting & Finance',
    'sequence': 3,
    'website' : 'http://clearcorp.co.cr',
    'images' : [],
    'depends' : [
                 'base',
                 'account',
                 ],
    'data' : [
              'view/account_invoice_move_discount_view.xml',
              ],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [],
    'test' : [],
    'auto_install': False,
    'application': False,
    'installable': True,
    'license': 'AGPL-3',
}