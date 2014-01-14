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
    'name': 'Account Asset extended ccorp',
    'version': '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'normal',
    'website': 'http://clearcorp.co.cr',
    'category': 'Accounting & Finance',
    'description': """
Extend account asset
==========================================
Create relation asset with invoice line.
Add model, asset number and responsible in assets.
Modify in the creation of several assets on an invoice line.
    """,
    'depends': ['account_asset'],
    'init_xml': [],
    'demo_xml': [],
    'data': [
             'security/ir.model.access.csv',
             'account_asset_extended_ccorp_view.xml',
             'report/extended_asset_report_view.xml',
             ],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
