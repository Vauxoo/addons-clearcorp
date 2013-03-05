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
from osv import fields, osv
from tools.translate import _
import netsvc
#from tools import debug
from dateutil import parser
from datetime import date

class rent_check_invoicing(osv.osv_memory):
	_name = "rent.check.invoicing"
	_description = "Force the verficiation of invoices until today"

	def fields_view_get(self, cr, uid, view_id=None, view_type='form', 
                        context=None, toolbar=False, submenu=False):
		""" 
		Changes the view dynamically
		@param self: The object pointer.
		@param cr: A database cursor
		@param uid: ID of the user currently logged in
		@param context: A standard dictionary 
		@return: New arch of view.
		"""
		if context is None:
			context={}
		res = super(rent_check_invoicing, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
		log_id = self.pool.get('rent.invoice.log').search(cr,uid,[],order='log_date desc')
		if log_id:
			last_log = self.pool.get('rent.invoice.log').browse(cr,uid,log_id[0])
			last_log = parser.parse(last_log.log_date).date()
		else:
			last_log = date.today()
			
		if last_log:
			try:
				desc = 'You are about to run the check for invoicing, the last date registered is: %s' % (last_log.strftime("%A %d %B %Y"))
		
				desc = """<label string='"""+desc+"""'/>"""
				arch1 = """<form string="Check rent invoicing to date">\n<separator string="Check Rent Invoicing" colspan="4"/>\n"""
				arch2 = """\n<group colspan="4" col="6">\n<button icon="gtk-cancel" special="cancel" string="Close"/>\n<button icon="terp-camera_test" string="Check Invoicing" name="check_invoicing" type="object" default_focus="1"/>\n</group>\n</form>"""
				arch_total = arch1 + desc + arch2
				#debug(arch_total)
				res['arch'] = arch_total
			except:
				return res
		return res
		
	def check_invoicing(self, cr, uid, ids=[], context=None):
		obj_rent = self.pool.get('rent.rent')
		obj_rent.cron_rent_invoice(cr,uid,ids,context=context)
		return {'type': 'ir.actions.act_window_close'}
rent_check_invoicing()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
