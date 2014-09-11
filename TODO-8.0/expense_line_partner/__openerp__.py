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
    'name': 'Expense line partner',
    'version': '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'normal',
    'website': 'http://clearcorp.co.cr',
    'category': 'Human Resources',
    'description': """
Extends hr_expense
===============================================
Adds partner field to choose supplier for a given expense line, At the account move line creation, sets 
the chosen partner for that given line instead of the hr_expense supplier  
""",
    'depends': ['hr_expense'],
    'init_xml': [],
    'demo_xml': [],
    'data': [
             'expense_line_partner_view.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
