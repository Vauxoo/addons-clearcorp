# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Commission',
    'version': '8.0.1.1',
    'category': 'Sales Management',
    'sequence': 3,
    'summary': 'Commissions over Sales',
    'author': 'ClearCorp',
    'website': 'http://clearcorp.co.cr',
    'complexity': 'normal',
    'images': [],
    'depends': [
                'sale',
                'account_invoice_discount',
                ],
    'data': [
             'data/report_paperformat.xml',
             'security/sale_commission_security.xml',
             'security/ir.model.access.csv',
             'sale_commission_view.xml',
             'sale_commission_menu.xml',
             'views/report_sale_commission.xml',
             'sale_commission_report.xml',
             'wizard/wizard.xml',
             ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
