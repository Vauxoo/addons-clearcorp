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
    "name" : 'Account Exchange Rates Adjustment',
    "version" : '1.0',
    "author" : 'CLEARCORP S.A',
    "category": 'Accounting & Finance',
    "description": """
Account Exchange Rates Adjustment:
====================================
    Adjust the amount of currency, 
    at the exchange rate on a specified day
    """,    
    "depends" : [
                 "account_report_lib",
                 "currency_rate_update_BCCR", 
                 "res_currency_sequence",
                ],

    "data" : [
                "wizard/account_exchange_rates_adjustment.xml",
                "account_exchange_rates_adjustment.xml",                 
                ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
