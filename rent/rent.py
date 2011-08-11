from osv import osv, fields
from tools import debug
import time
import constanst

#Class that inherits from res.partner allowing to record the 
#necesary data from the clients

class rent_client(osv.osv):
	_name = 'rent.client'
	_inherit = 'res.partner'
	_columns = {
		#'client_lastname'  : fields.char('Lastname',size=15,required=True),
		#'client_lastname2' : fields.char('Second Lastname',size=15,required=True),
		#'partner_id'        : fields.char('Id',size=10,required=True,help='Cedula del cliente'),
		
		'client_birthdate' : fields.date('Birthdate',select=1,required=True),
		#'client_location'  : fields.one2many('rent.location','location_id','Location'),
		#'client_province' : fields.selection((('Alajuela', 'Alajuela'),('Cartago','Cartago'),('Guanacaste','Guanacaste'),('Heredia','Heredia'),
		#										('Limon', 'Limon'),('San Jose', 'San Jose'),('Puntarenas', 'Puntarenas')),'Province', required=True),
		'client_canton'    : fields.related('address', 'location_canton', type='char', string='Canton'),
		'client_district'  : fields.related('address', 'location_district', type='char', string='District'),
	}
rent_client()

class rent_location(osv.osv):
	_name = 'res.partner.address'
	_inherit = 'res.partner.address'
	_columns = {
		#'location_id'       : fields.many2one('rent.client','Client ID'),
		'province'          : fields.selection((('Alajuela', 'Alajuela'),('Cartago','Cartago'),('Guanacaste','Guanacaste'),('Heredia','Heredia'),
												('Limon', 'Limon'),('San Jose', 'San Jose'),('Puntarenas', 'Puntarenas')),'Province', required=True),
		'canton'   : fields.char('Canton',size=20,required=True),
		'district' : fields.char('District',size=20,required=True),
	}
	def determine_canton(self,cr,uid,ids,pField,context=None):
		v = {}
		debug('asiiiiiiiiiiiiiiii')
		debug(pField)
		try:
			v['canton'] = {
				'San Jose'   : constanst.SJ_CANTON,
				'Heredia'    : constanst.H_CANTON, 
				'Alajuela'   : constanst.A_CANTON,
				'Cartago'    : (()),
				'Puntarenas' : (()),
				'Limon'      : (()),
				'Guanacaste' : (()),
			}[pField]
			debug(v)
		except KeyError:
			debug('se cae')
		return { 'value':v}
	def determine_district(self,cr,uid,ids,context=None):
		v = {}
		v['district'] = (())
		return {'value':v}
rent_location()

class rent_state(osv.osv):
	_name = 'rent.state'
	_rec_name = "state_number"
	_columns = {
		'state_province' : fields.selection((('Alajuela', 'Alajuela'),('Cartago','Cartago'),('Guanacaste','Guanacaste'),('Heredia','Heredia'),
											('Limon', 'Limon'),('San Jose', 'San Jose'),('Puntarenas', 'Puntarenas')),'Province', required=True),
		'state_canton'   : fields.selection((),'Canton',required=True),
		'state_district' : fields.selection((),'District', required=True,readonly=True),
		'state_number'   : fields.char('# State', size=10,required=True),
		'state_value'    : fields.float('Value',required=True),
		'state_area'     : fields.float('Area', required=True),
		'state_buildings': fields.one2many('rent.building','building_estate','Buildings'),
		'state_location' : fields.one2many('rent.location','partner_id','Location'),
		#'state_address'  : fields.one2many('res.partner.address','partner_id', 'Direccion'),
		#'state_province': fields.related('state_address', 'state_province', type='selection', string='Province'),
        #'state_canton': fields.related('state_address', 'state_canton', type='selection', string='Canton'),
        #'state_district': fields.related('state_address', 'state_district', type='selection', string='District'),
	}
	
	
rent_state()


class rent_building(osv.osv):
	_name = 'rent.building'
	_columns = {
		'building_capacity'          : fields.integer('Capacity',required=True),
		'building_date_construction' : fields.date('Construction Date', required=True),
		'building_elevator'          : fields.boolean('Elevadores',help='Select if the building has at least one elevator'),
		'building_elevators_number'  : fields.integer('Elvetators number',help='If checkbox of elevators is no selected this will be 0'),
		'building_stairs'            : fields.boolean('Stairs',help='Select if the building has at least one elevator'),
		'building_stairs_type'       : fields.integer('Stairs number',help='If checkbox of stairs is no selected this will be 0'),
		'name'                       : fields.char('Name', size=40,required=True),
		'building_value'             : fields.float('Value'),
		'building_area'              : fields.float('Area'),
		'building_estate'            : fields.many2one('rent.state', 'State'),
	}
rent_building()

class rent_floor(osv.osv):
	_name = 'rent.floor'
	_columns = {
		'floor_number' : fields.integer('# Floor',required=True),
	}
rent_floor()

