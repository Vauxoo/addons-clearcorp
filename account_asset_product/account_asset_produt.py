from osv import osv, fields
from tools import debug
import time
import pooler
from dateutil import parser
from datetime import date
from datetime import timedelta
import calendar
from tools.translate import _


class ccorp_addons_ir_sequence(osv.osv):
	_name = 'ir.sequence'
	_inherit = 'ir.sequence'
	
	def get_id_search(self, cr, uid, sequence_id, test='id', context=None):
		assert test in ('code','id')
		company_ids = self.pool.get('res.company').search(cr, uid, [], context=context)
		cr.execute('''SELECT id, number_next, prefix, suffix, padding
					FROM ir_sequence
					WHERE %s=%%s
					AND active=true
					AND (company_id in %%s or company_id is NULL)
					ORDER BY company_id, id
					FOR UPDATE NOWAIT''' % test,
					(sequence_id, tuple(company_ids)))
		res = cr.dictfetchone()
		if res:
			if res['number_next']:
				return self._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + self._process(res['suffix'])
			else:
				return self._process(res['prefix']) + self._process(res['suffix'])
		return False
ccorp_addons_ir_sequence()



class ccorp_addons_account_assets(osv.osv):
	_name = 'account.asset.asset'
	_inherit = 'account.asset.asset'
	_columns = {
		'product_id': fields.many2one('product.product', 'Product'), #, domain=[('type', '<>', 'service')]
		'location_id': fields.dummy(string='Stock Location', relation='stock.location', type='many2one'),
		'prod_lot_id': fields.many2one('stock.production.lot', 'Production Lot', domain="[('product_id','=',product_id)]"),
	}
	_defaults = { 
		'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get_id_search(cr, uid, 'account.asset.code')
	}
ccorp_addons_account_assets()





