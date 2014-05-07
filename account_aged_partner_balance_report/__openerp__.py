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
    'name': 'Account Aged Partner Balance Report',
    'version': '1.0',
    'author': 'CLEARCORP S.A.',
    'category': 'Accounting & Finance',
    'description': """
Account Aged Partner Balance Report.
======================================
This module permits to print a Aged Partner Balance Report.
""",
    'website': 'http://clearcorp.co.cr',
    'depends': ['account','account_report_lib',],
    'data': [
             'security/ir.model.access.csv',
             'wizard/account_aged_partner_balance_report_wizard.xml',
             'report/report.xml',
             'report_menus.xml',
            ],
    'active': False,
    'installable': True,    
    'license': 'AGPL-3',
}
