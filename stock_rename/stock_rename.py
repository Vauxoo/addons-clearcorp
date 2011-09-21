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
		for obj_stock_location in self.browse(cr,uid,ids):
			data = []
			location = obj_stock_location
			is_leaf = True
			while location:
				debug(data)
				if not location.location_id or is_leaf:
					data.insert(0,location.name)
					is_leaft = False
				else:
					data.insert(0,(location.shortcut or location.name))
				location = location.location_id
			debug("DATA FINAL")
			data = '/'.join(data)
			debug(data)
			res.append((location.id, data))  
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
