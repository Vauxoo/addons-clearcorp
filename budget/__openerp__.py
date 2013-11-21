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
    'name': 'Public Budget',
    'version': '0.1',
    'url': 'http://launchpad.net/openerp-ccorp-addons',
    'author': 'ClearCorp S.A.',
    'website': 'http://clearcorp.co.cr',
    'category': 'Generic Modules/Base',
    'description': """ This module adds the logic for Public Budget management and it's different processes
    """,
    'depends': [
        'base',
        'account',
        'purchase',
        'sale',
        'purchase_order_discount',
        'hr_payroll',
        'hr_payroll_account',
        'hr_expense',
        'account_account_extended_ccorp',
        'expense_line_partner'
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'budget_workflow.xml',
        'wizard/budget_program_populate_view.xml',
        'budget_view.xml',
        'wizard/budget_import_catalog_view.xml',
        'res_partner_view.xml',
        'budget_sequence.xml',
        'account_invoice_view.xml',
        'account_view.xml',
        'account_move_line.xml',
        'hr_expense_view.xml',
        'hr_expense_workflow.xml',
        'purchase_view.xml',
        'purchase_workflow.xml',
        'hr_payroll.xml'
#        'sale_view.xml'
        ],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
    'application': True,

}
