# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Order Report',
    'summary': 'Sale order report in Qweb',
    'version': '8.0.1.0',
    'category': 'Sales',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    "depends": [
        'sale_order_discount',
        'sale_order_extended',
        'base_reporting',
        ],
    "data": [
        'data/report.paperformat.xml',
        'data/sale_report.xml',
        'views/report_sale_order.xml',
        'views/report_sale_order_layout.xml',
        'views/report_sale_order_layout_header.xml',
        'views/report_sale_order_layout_footer.xml',
    ],
}
