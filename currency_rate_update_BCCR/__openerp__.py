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
    'name': 'Currency Rate Update BCCR',
    'version': '1.0',
    'author': 'CLEARCORP S.A.',    
    'category': 'Generic Modules/Base',
    'description': """
Import exchange rates from BCCR.
==================================
    This module permits for each currency, create a process that will update 
    exchange range. You can adapt this process depends of your needs.
    Also, it will create a link between process and currency, update data each
    time that someone change.
    """,
    'depends': [
                'res_currency_sequence',
                'currency_rate_update',
                ],
    'data': [
             'security/ir.model.access.csv',
             'company_view.xml',
             'res_currency_view.xml',
             ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
