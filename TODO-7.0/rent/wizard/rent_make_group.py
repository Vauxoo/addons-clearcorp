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

class rent_make_group(osv.osv_memory):
	_name = "rent.make.group"
	_columns = {
		'name'            : fields.char('Name',size=64,required=True),
		#'code'            : fields.char('Code',size=64, help='sequence auto generated for the contrat', readonly=True),
	}
	_defaults = {
		'name'    : 'Contract group',
		#'code'    : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'rent.rent.group'),
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
					'message' : 'The contract already has a group. You can not proceed, the previous will remain.'
				}
			}
		return False

	def make_group(self, cr, uid, ids, context=None):
		obj_rent = self.pool.get('rent.rent')
		obj_group = self.pool.get('rent.rent.group')
		if context is None:
			context = {}
		data = self.read(cr, uid, ids)[0]
		newgrp = False
		for o in obj_rent.browse(cr, uid, context.get(('active_ids'), []), context=context):
			group_ids =self.pool.get('rent.rent.group').search(cr,uid,[],context=context)
			created = False
			for group_id in self.pool.get('rent.rent.group').browse(cr,uid,group_ids,context=context):
				if group_id.name == data['name']:
					created = True
					newgrp = group_id.id
					break
			if created == False:
				vals = {
						'name'     : data['name'],
						'obj_rent' : o.id,
				}
			newgrp = obj_group.create(cr,uid,vals,context)
			#debug(newgrp)
			o.write({'rent_group_id':newgrp})
		return {'type': 'ir.actions.act_window_close'}
rent_make_group()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
