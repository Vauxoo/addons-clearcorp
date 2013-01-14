# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by SIESA
#    Copyright (C) 2009-TODAY Soluciones Industriales Electromecanicas S.A. (<http://siesacr.com>).
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
    "name" : "MRP Bom Updater",
    "version" : "1.0",
    "author" : "SIESA",
    "category" : "Generic Modules/Inventory Control",
    "depends" : ["procurement", "stock", "resource", "purchase", "product","process","mrp"],
    'complexity': "easy",
    "website" : "http://www.siesacr.com",
    "description": """
            This module update the price of 1 product when BOM is created.
    """,
    'update_xml': [

    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
