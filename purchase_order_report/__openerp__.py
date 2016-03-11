# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Order Report',
    'summary': 'The purchase order request for quotation report',
    'version': '8.0.1.0',
    'category': 'Purchase Management',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'purchase',
        'purchase_order_discount',
        'base_reporting',
    ],
    'data': [
        'data/report_paperformat.xml',
        'data/purchase_report.xml',
        'views/report_purchase_order.xml',
        'views/report_purchasequotation.xml',
        'views/report_purchase_layout_footer.xml',
        'views/report_purchase_layout_header.xml',
        'views/report_purchase_layout.xml',
    ],
}
