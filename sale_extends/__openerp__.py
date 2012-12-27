##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    "name":"Sales Order Extends",
    "version":"1.0",
    "category" : "Generic Modules/Sales & Purchases",
    "description": """
This module adds=
    # sale order validity
    # client purchase order required
    # sale order part number
    # client credit check before invoice create
    # update sale order line qty to stock available
    # add delivery time to sale order line
    # remove change_product_id in product_uom_qty
    """,
    "author":"SIESA",
    "depends":['sale','account_invoice_extends','partner_extends'],
    "demo_xml":[],
    "update_xml":['wizard/sale_change_currency_view.xml',
                   'sale_view.xml',
                   'sale_commision_view.xml',
                   'commision_sequence.xml',
                   'sale_commission_workflow.xml'
                  ],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

