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
    'name': 'Account report signatures',
    'version': '0.1',
    'url': 'http://launchpad.net/openerp-ccorp-addons',
    'author': 'ClearCorp S.A',
    'website': 'http://clearcorp.co.cr',
    'category': 'Generic Modules/Base',
    'description': """ Add the users that can signature the reports.""",
    'depends': ['base', 'account','hr'],
    'init_xml': [],
    'demo_xml': [],
    'data': [ 'security/account_report_signatures_security.xml',
              'account_report_signatures.xml',
              'account_report_signature_menu.xml'],
    'license': 'Other OSI approved licence',
    'installable': True,
    'active': False,
}
