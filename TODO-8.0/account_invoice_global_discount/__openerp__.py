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
    "name" : 'Global invoice discount',
    "version" : '1.0',
    "author" : 'CLEARCORP S.A',
    'complexity': 'normal',
    "description": """
Adds a discount feature for invoice.

With it one can add a discount percent to all invoice lines on an invoice.
It adds the discounted and undiscounted amounts on the invoice totals.
    """,
    "category": 'Accounting & Finance',
    "sequence": 4,
    "website" : "http://clearcorp.co.cr",
    "images" : [],
    "icon" : False,
    "depends" : ['account',
                'product_visible_discount'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [],
    "data" : [
        'account_invoice_global_discount_view.xml',
        'wizard/discount_wizard_view.xml',
    ],
    "test" : [],
    "auto_install": False,
    "application": False,
    "installable": True,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
