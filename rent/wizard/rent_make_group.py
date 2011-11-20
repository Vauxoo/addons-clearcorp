# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-PRESENT CLEARCORP S.A. (<http://www.clearcorp.co.cr>).
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

class rent_make_group(osv.osv_memory):
	_name = "rent.make.group"
	_description = "Rent Make Group"
	_columns = {
		'code'            : fields.char('Code', help='Check the box to group the invoices for the same customers'),
		'name'            : fields.char('Name',size=64,required=True),
	}
	_defaults = {
		'name'    : 'Contract group'
	}

	def view_init(self, cr, uid, fields_list, context=None):
		if context is None:
			context = {}
		record_id = context and context.get('active_id', False)
		obj_rent = self.pool.get('rent.rent').browse(cr, uid, record_id, context=context)
		if obj_rent.state == 'draft':
			raise osv.except_osv(_('Warning !'),'You can not create an group when rent is not confirmed.')
		if obj_rent.rent_group_id:
			return {
				'warning' : {
					'title' : 'Alert',
					'message' : 'The contract already has a group. If you proceed, the previous group will be overwrited'
				}
			}
		return False

	def make_group(self, cr, uid, ids, context=None):
		order_obj = self.pool.get('sale.order')
		mod_obj = self.pool.get('ir.model.data')
		newinv = []
		if context is None:
			context = {}
		data = self.read(cr, uid, ids)[0]
		order_obj.action_invoice_create(cr, uid, context.get(('active_ids'), []), data['grouped'], date_inv = data['invoice_date'])
		wf_service = netsvc.LocalService("workflow")
		for id in context.get(('active_ids'), []):
			wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)

		for o in order_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
			for i in o.invoice_ids:
				newinv.append(i.id)

		res = mod_obj.get_object_reference(cr, uid, 'account', 'view_account_invoice_filter')

		return {
			
		}

rent_make_group()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
