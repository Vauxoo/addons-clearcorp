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
    "name" : 'Account object (account.account) rename',
    "version" : '1.0',
    "author" : 'CLEARCORP S.A',
    'complexity': 'normal',
    "description": """
This module simply renames the financial account. It makes uses of the company shortcut (provided by "base_company_prefix" module) and the account shortcut field.

The account will appear as:
CP-CODE SRT2/SRT3/.../SRTn-1/NAME

CP:   Company prefix
CODE: Account code
SRT2: Account shortcut for the second parent (being the account without parent the first)
SRTX: Next account shortcuts for the account hierarchy
NAME: Account name
    """,
    "category": 'Accounting & Finance',
    "sequence": 4,
    "website" : "http://clearcorp.co.cr",
    "images" : [],
    "icon" : False,
    "depends" : ["account","base_company_prefix"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["account_rename_view.xml"],
    "test" : [],
    "auto_install": False,
    "application": False,
    "installable": True,
}