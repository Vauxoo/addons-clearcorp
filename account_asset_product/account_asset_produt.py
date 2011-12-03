from osv import osv, fields
from tools import debug
import time
import pooler
from dateutil import parser
from datetime import date
from datetime import timedelta
import calendar
from tools.translate import _



class ccorp_addons_account_assets(osv.osv):
	_name = 'account.asset.asset'
	_inherit = 'account.asset.asset'
	
	
	def _getCompany(self, cr, uid, vals, context=None):
		user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid], context=context)[0]
		if user.company_id:
			return user.company_id.id
	
	# Metodos de  ir.sequence
	# se utilizan para poder traer el numero de secuencia sin incrementarlo.
	
	def _process(self, s):
		return (s or '') % {
			'year':time.strftime('%Y'),
			'month': time.strftime('%m'),
			'day':time.strftime('%d'),
			'y': time.strftime('%y'),
			'doy': time.strftime('%j'),
			'woy': time.strftime('%W'),
			'weekday': time.strftime('%w'),
			'h24': time.strftime('%H'),
			'h12': time.strftime('%I'),
			'min': time.strftime('%M'),
			'sec': time.strftime('%S'),
		}
	
	
	
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

	
	def get_search(self, cr, uid, context=None):
		code='account.asset.asset'
		return self.get_id_search(cr, uid, code, test='code')
	
	#################################33
	
	
	
	_columns = {
		'prod_lot_id': fields.many2one('stock.production.lot', 'Production Lot'), #, domain="[('company_id','=',product_id)]",
		'asset_product_id': fields.related('prod_lot_id', 'product_id', type='many2one', relation='product.product', string='Product', readonly=True),
		'location_id': fields.related('prod_lot_id', 'last_location_id', type='many2one', relation='stock.location', string='Location', readonly=True),
		
	}
	
	_defaults = { 
		'code': get_search,
		'partner_id': _getCompany
	}
	
	_sql_constraints = [ 
		('unique_asset_company', 'UNIQUE (partner_id,code)', 'You can not have two asset with the same code in the same partner !') 
	] 
	
	# Metodo: Create
	#Descripcion: 
	#		Revisa que el codigo que se quiere guardar sea igual al autogenerado si lo es incrementa el secuencial 
	# 		si no lo es no incrementa el secuencial y lo guarda como viene.
	#
	def create(self, cr, uid, vals, context=None):
		sentCode = vals['code']
		debug(sentCode)
		if sentCode == self.get_search(cr, uid, 'account.asset.asset'):
			codep=self.pool.get('ir.sequence').get(cr, uid, 'account.asset.asset')
		return super(ccorp_addons_account_assets, self).create(cr, uid, vals, context=None)
	
ccorp_addons_account_assets()





