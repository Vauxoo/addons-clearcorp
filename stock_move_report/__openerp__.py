# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Move Report',
    'summary': 'Module summary',
    'version': '9.0.1.0',
    'category': 'Warehouse Management',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'stock',
        'product',
        # 'report_xls_template'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        # 'views/stock_move_report_report.xml',
        # 'views/stock_move_order_report.xml',
        'views/report_stock_move_pdf.xml',
        'report/stock_move_analysis_view.xml',
        # 'views/report_stock_move_xls.xml',
        # 'views/report_stock_move_order.xml',
        'wizard/stock_move_report_wizard_view.xml',
        'wizard/stock_move_order_wizard_view.xml'
    ],
}
