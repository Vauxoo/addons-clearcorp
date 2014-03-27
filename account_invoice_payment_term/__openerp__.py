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
    'name' : 'Account Invoice Payment Term',
    'version' : '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'easy',
    'description': '''
Partner Credit Validation
=========================
Check and verify the total credit amount when validating Sale Orders and Customer Invoices.

Main Features
-------------
* Unlimited Payment group to allow users exceed the credit limit
* Validation of Partner total credit on Sale Orders and Customer Invoices
''',
    'category': 'Accounting & Finance',
    'sequence': 3,
    'website' : 'http://clearcorp.co.cr',
    'images' : [],
    'depends' : [
                 'base',
                 'account',
                 'sale'
                 ],
    'data' : [
              'security/account_invoice_payment_term_security.xml',
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