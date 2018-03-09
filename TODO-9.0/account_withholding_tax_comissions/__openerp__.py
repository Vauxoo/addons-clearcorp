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
    'name': 'Account Withholding Tax',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'description': """
Account Withholding Taxes:
==========================
Description:
-------------
        1. Add object account.withholding.tax
        2. Manage account.withholding tax for accounts. 
        3. Add withholding taxes for supplier and customer voucher.""",
    'author': 'ClearCorp',
    'website': 'http://www.clearcorp.co.cr',
    'depends': [
                'account',
                'account_voucher',
                'account_move_reverse',
                'account_voucher_reverse',
                ],
    'data': [
             'withholding_tax.xml',
             'account_journal.xml',
             'account_voucher.xml',
             'security/ir.model.access.csv',
             ],
    'installable': False,
    'auto_install': False,
}
