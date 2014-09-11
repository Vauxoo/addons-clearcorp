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
    "name" : 'Exchange Rate Calculated',
    "version" : '1.0',
    "author" : 'CLEARCORP S.A.',
    'category': 'Accounting & Finance',
    "description": """
Exchange Rate Calculated:
==========================
This module permits, in manual account moves, it will compute the amount currency 
and it applies the exchange rate for selected currency. I will assign the amount 
in debit or credit field, if amount currency is negative, it will be credit and 
if it is positve, it will be debit.
""",
    "website" : "http://clearcorp.co.cr",
    "depends" : ['account',],
    "data" : [
              'account_move_line.xml',
             ],
    'active': False,
    'installable': True,    
    'license': 'AGPL-3',
}
