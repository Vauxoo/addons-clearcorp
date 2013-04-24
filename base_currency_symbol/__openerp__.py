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
	'name': 'Base currency symbol',
	'version': '1.0',
	'url': 'http://launchpad.net/openerp-ccorp-addons',
	'author': 'ClearCorp S.A.',
	'website': 'http://clearcorp.co.cr',
	'category': 'General Modules/Base',
	'description': """Adds symbol to currency:
					  Use symbol_prefix and symbol_suffix depending on the currency standard.
				   """,
	'depends': ['base'],
	'init_xml': [],
	'demo_xml': [],
	'update_xml': [
		'base_currency_symbol_data.xml',
		'base_currency_symbol_view.xml',
		],
	'license': 'Other OSI approved licence',
	'installable': True,
	'active': False,
}
