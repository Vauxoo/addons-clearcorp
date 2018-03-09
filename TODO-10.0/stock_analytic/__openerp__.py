# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock analytic",
    "summary": "Adds an analytic account in stock move",
    "version": "9.0.1.0",
    "author": "Julius Network Solutions,"
    "ClearCorp, Odoo Community Association (OCA)",
    "website": "http://www.julius.fr/",
    'complexity': "easy",
    "category": "Warehouse Management",
    "depends": [
        "base",
        "stock",
        "sale",
        "purchase",
        "analytic",
        "sale_stock",
    ],
    "data": [
        "views/stock_view.xml",
    ],
    'installable': False,
    'active': False,
}
