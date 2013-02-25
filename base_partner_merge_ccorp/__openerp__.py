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
# 

{
    'name': 'Partner Merger CLEARCORP',
    'version': '1.0',
    'category': 'Generic Modules/Base',
    'description': """
Originally developed by Tiny SPRL.
Fixed, improved and adapted to V6 by Guewen Baconnier - Camptocamp 2011
This module has been adopted by CLEARCORP from the extra-trunk repository
To merge 2 partners, select them in the list view and execute the Action "Merge Partners".
To merge 2 addresses, select them in the list view and execute the Action "Merge Partner Addresses" or use the menu item :
 Partners / Configuration / Merge Partner Addresses

The selected addresses/partners are deactivated and a new one is created with :
 - When a value is the same on each resources : the value
 - When a value is different between the resources : you can choose the value to keep in a selection list
 - When a value is set on a resource and is empty on the second one : the value set on the resource
 - All many2many relations of the 2 resources are created on the new resource.
 - All the one2many relations (invoices, sale_orders, ...) are updated in order to link to the new resource.

    """,
    'author': 'CLEARCORP',
    'website': 'http://www.clearcorp.co.cr',
    'depends': ['base','base_partner_sequence_ccorp'],
    'init_xml': [],
    'update_xml': [
                    "wizard/base_partner_merge_ccorp_view.xml", 
                    "wizard/base_partner_merge_address_ccorp_view.xml"
                   ],
    'demo_xml': [],
    'installable': True,
    "active": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
