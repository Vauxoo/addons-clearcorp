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

from osv import osv,fields

class res_currency(osv.osv):
	'''
	Adds symbol fields to currency to provide better reporting.
	'''
	_inherit = 'res.currency'
	
	_columns = {
		'symbol_prefix':fields.char('Symbol prefix', size=16, required=False, readonly=False, translate=False, select=2, help="Currency symbol printed BEFORE amount. Include the trailing space if needed."),
		'symbol_suffix':fields.char('Symbol suffix', size=16, required=False, readonly=False, translate=False, select=2, help="Currency symbol printed AFTER amount. Include the leading space if needed."),
		'currency_name':fields.char('Currency name', size=16, required=False, readonly=False, translate=False, select=2, help="Name of the currency printed AFTER amount. Allowing to use it at amount to text convertions"),
	}
res_currency()
