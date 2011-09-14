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
		reads = self.read(cr, uid, ids, ['name','location_id'], context=context)
		for record in reads:
			name = record['name']
			if context.get('full',False):
				if record['location_id']:
					name = record['location_id'][1] + ' / ' + name
				res.append((record['id'], name))
			else:
				debug("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
				if record['location_id']:
					if len(record['location_id'][1].split(',')) < 2:
						obj_stock_location = self.browse(cr,uid,record['location_id'][0])
						debug(obj_stock_location)
						if obj_stock_location.shortcut:
							name = obj_stock_location.shortcut + '--' + name
						else:
							name = name + ', ' + record['location_id'][1]
				res.append((record['id'], name))
		return res
	
	_columns = {
		'shortcut'  :  fields.char('Shortcut',size=10),
	}
stock_location()
