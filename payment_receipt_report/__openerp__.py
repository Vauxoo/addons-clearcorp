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
    'name': 'Payment Receipt Report Webkit',
    'version': '1.0',
    'url': 'http://launchpad.net/openerp-ccorp-addons',
    'author': 'ClearCorp S.A.',
    'website': 'http://clearcorp.co.cr',
    "category": 'Accounting & Finance',
    'description': """Module that create Voucher Report """,
    'depends': [
        'account',
        'account_voucher_payment_method',
        'base_currency_symbol',
        'account_report_lib',
        ],
    'init_xml': [],
    'update_xml': [
        'data/payment_receipt_report_webkit.xml',
        'payment_receipt_report.xml', 
        ],
   'license': 'AGPL-3',
    'installable': True,
    'active': False,
}
