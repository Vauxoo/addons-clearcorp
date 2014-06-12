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
    'name' : 'Account Invoice Payment Term Date Due Security',
    'version' : '1.0',
    'author' : 'CLEARCORP S.A.',
    'category': 'Accounting & Finance',
    'description': """
Account Invoice Payment Term Date Due Security
=================================================
This module adds security to payment term and date due in invoice. Also,
it adds security on payment term in sale order
""",    
    'website' : 'http://clearcorp.co.cr',
    'depends' : ['base','account','sale','purchase'],
    'data' : [
              'security/account_invoice_payment_term_date_due_security.xml',
              'account_invoice_inherit.xml',
              'sale_order_inherit.xml',
              'purchase_order_inherit.xml',
              ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}