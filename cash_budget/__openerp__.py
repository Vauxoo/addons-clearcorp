# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cash Budget',
    'version': '8.0.1.2',
    'summary': "Goverment Institutions Cash Budget",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.cr',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'account_account_extended_ccorp',
        'account_distribution_line',
        'account',
        'expense_line_partner',
        'hr_expense',
        'hr_payroll_account',
        'hr_payroll',
        'purchase_order_discount',
        'purchase',
        'sale_stock',
        'sale',
        ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
        'views/account_move_line.xml',
        'views/account_view.xml',
        'views/cash_budget_sequence.xml',
        'views/cash_budget_view.xml',
        'views/cash_budget_workflow.xml',
        'views/hr_expense_view.xml',
        'views/hr_expense_workflow.xml',
        'views/hr_payroll.xml',
        'views/purchase_view.xml',
        'views/purchase_workflow.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'wizard/cash_budget_import_catalog_view.xml',
        'wizard/cash_budget_program_populate_view.xml',
        'data/cash_budget_data.xml'
    ]
}
