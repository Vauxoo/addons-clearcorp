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
    "name" : "Magento-OpenERP Stadistic",
    "version" : "1.0",
    "author" : "Clearcorp",
    "license": 'AGPL-3',
    'author': 'CLEARCORP S.A.',
    'complexity': 'normal',
    "description": """
        Magento-Openerp Stadistic
        ======================
        Magento-OpenERP Stadistic. Generate reports and graphics for a failed magento sales and missing product in Magento Store
        """,
    "category" : "Interfaces/CMS & eCommerce",
    "sequence": 4,
    'website': 'http://www.clearcorp.co.cr',
    "images" : [],
    "depends" : ["product", "stock", "sale", "account", "account_analytic_default","sneldev_magento"],
    "init_xml" : [],
    "icon" : "icon.png",
    "demo_xml" : [],
    "update_xml" :  ['magento_stadistic_view.xml',
                     'magento_stadistic_menu.xml',                     
                     ],
    "active": False,
    "installable": True
}
