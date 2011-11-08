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

	def get_search(self, cr, uid, code):
		return self.get_id_search(cr, uid, code, test='code')

ccorp_addons_ir_sequence()



class ccorp_addons_account_assets(osv.osv):
	_name = 'account.asset.asset'
	_inherit = 'account.asset.asset'
	
	def _getCompany(self, cr, uid, vals, context=None):
		user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid], context=context)[0]
		if user.company_id:
			return user.company_id.id
	
	def get_location1(self, cr, uid, ids, pprodlot, context=None):
		product_lot= self.pool.get('stock.production.lot').browse(cr, uid, pprodlot)
		debug(product_lot)
		#debug(product_lot.product_id)
		res = {}
		saved_move_location = 0
		saved_move_date = 0
		
		
		for move_object in product_lot.move_ids:
			#debug(key)
			#move_object= self.pool.get('stock.move').browse(cr, uid, key)
			debug(move_object)
			debug(move_object.date)
			temp_saved_move_date = parser.parse(move_object.date).date()
			if saved_move_date == 0:
				saved_move_location = move_object.location_id.name
				saved_move_date = parser.parse(move_object.date).date()
				
			elif saved_move_date <= temp_saved_move_date:
				saved_move_location = move_object.location_id.name
				saved_move_date = parser.parse(move_object.date).date()
			
		
		return saved_move_location
	
	
	def get_product1(self, cr, uid, ids, pprodlot, context=None):
		product_lot= self.pool.get('stock.production.lot').browse(cr, uid, pprodlot)
		debug(product_lot)
		#debug(product_lot.product_id)
		saved_lot_product= product_lot.product_id.name
		
		
		
		return saved_lot_product
	
	_columns = {
		'prod_lot_id': fields.many2one('stock.production.lot', 'Production Lot'), #, domain="[('company_id','=',product_id)]",
		'asset_product_id': fields.char(size=100 ,string='Product', readonly=True ),
		'location_id': fields.char(size=100 ,string='Location', readonly=True ),
		
	}
	_defaults = { 
		'code': lambda self, cr, uid, context: self.pool.get('ir.sequence').get_search(cr, uid, 'account.asset.asset'),
		'partner_id': _getCompany
	}
	_sql_constraints = [ 
		('unique_asset_company', 'UNIQUE (partner_id,code)', 'You can not have two asset with the same code in the same partner !') 
	] 
	
	def on_change_search_location(self, cr, uid, ids, pprodlot):
		result = self.get_location1(cr,uid, ids,pprodlot)
		result2 = self.get_product1(cr,uid, ids,pprodlot)
		v = {}
		v['location_id'] = result
		v['asset_product_id'] = result2
		return {'value':v}
	
	
	
	
	def create(self, cr, uid, vals, context=None):
		sentCode = vals['code']
		debug(sentCode)
		if sentCode == (self.pool.get('ir.sequence').get_search(cr, uid, 'account.asset.asset')):
			codep=self.pool.get('ir.sequence').get(cr, uid, 'account.asset.asset')
		return super(ccorp_addons_account_assets, self).create(cr, uid, vals, context=None)
	
ccorp_addons_account_assets()





