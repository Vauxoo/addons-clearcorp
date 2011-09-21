from osv import osv, fields
from tools import debug
import time
import pooler
from dateutil import parser
from datetime import date
import calendar
from tools.translate import _

class stock_location(osv.osv):
	_name = "stock.location"
	_inherit = "stock.location"
	
	def name_get(self, cr, uid, ids, context=None):
		res = []
		if context is None:
			context = {}
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['name','location_id','shortcut'], context=context)
		for record in reads:
			name = record['name']
			if record['location_id']:
				obj_stock_location = self.browse(cr,uid,record['location_id'][0])
				if obj_stock_location.shortcut:
					short_path = record['location_id'][1].strip(obj_stock_location.name)
					name = short_path + obj_stock_location.shortcut + ' / ' + name
				else:
					name = record['location_id'][1] + ' / ' + name
			res.append((record['id'], name))  
		return res
	
	def _complete_name2(self, cr, uid, ids, name, args, context=None):
		""" Forms complete name of location from parent location to child location.
		@return: Dictionary of values
		"""
		def _get_one_full_name(location, level=4):
			if location.location_id:
				parent_path = _get_one_full_name(location.location_id, level-1)
				if location.location_id.shortcut:
					short_path = parent_path.strip(location.location_id.name)
					parent_path = short_path + location.location_id.shortcut + ' / '
				else:
					parent_path = parent_path + ' / '
			else:
				parent_path = ''
			return parent_path + location.name
		res = {}
		for m in self.browse(cr, uid, ids, context=context):
			res[m.id] = _get_one_full_name(m)
		return res
	_columns = {
		'shortcut'  :  fields.char('Shortcut',size=10),
		'complete_name': fields.function(_complete_name2, method=True, type='char', size=100, string="Location Name"),
	}
stock_location()
