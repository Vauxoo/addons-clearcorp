from osv import osv, fields
from tools import debug
import time

#Class that inherits from res.partner allowing to record the 
#necesary data from the clients

class rent_client(osv.osv):
	_name = 'rent.client'
	_inherit = 'res.partner'
	_columns = {
		'client_lastname'  : fields.char('Lastname',size=15,required=True),
		'client_lastname2' : fields.char('Second Lastname',size=15,required=True),
		'client_birthdate' : fields.date('Birthdate',select=1,required=True),
		'client_province'  : fields.selection((('Alajuela', 'Alajuela'),('Cartago','Cartago'),('Guanacaste','Guanacaste'),('Heredia','Heredia'),
												('Limon', 'Limon'),('San Jose', 'San Jose'),('Puntarenas', 'Puntarenas')),'Province', required=True),
		'client_id'        : fields.char('Id',size=10,required=True,help='Cedula del cliente'),
	}
rent_client()

class rent_state(osv.osv):
	_name = 'rent.state'
	_rec_name = "state_number"
	_columns = {
		'state_province' : fields.selection((('Alajuela', 'Alajuela'),('Cartago','Cartago'),('Guanacaste','Guanacaste'),('Heredia','Heredia'),
											('Limon', 'Limon'),('San Jose', 'San Jose'),('Puntarenas', 'Puntarenas')),'Province', required=True),
		'state_canton'   : fields.selection((),'Canton',required=True,readonly=True),
		'state_district' : fields.selection((),'District', required=True,readonly=True),
		'state_number'   : fields.char('# State', size=10,required=True),
		'state_value'    : fields.float('Value',required=True),
		'state_area'     : fields.float('Area', required=True),
		'state_buildings': fields.one2many('rent.building','building_estate','Buildings'),
	}
	
	SJ_CANTON = (('San Jose','San Jose'), ('Escazu','Escazu'),('Desamparados','Desamparados'), ('Puriscal','Puriscal'),('Tarrazú','Tarrazú'),('Aserrí','Aserrí'),('Mora','Mora'), ('Goicoechea','Goicoechea'),('Santa Ana','Santa Ana'),('Alajuelita','Alajuelita'),('Vázquez de Coronado','Vázquez de Coronado'),('Acosta','Acosta'),('Tibás','Tibás'),('Moravia','Moravia'),('Montes de Oca','Montes de Oca'),('Turrubares','Turrubares'),('Dota','Dota'),('Curridabat','Curridabat'),('Pérez Zeledón','Pérez Zeledón'),('León Cortés','León Cortés'))
	
	def determine_canton(self,cr,uid,ids,pField,context=None):
		v = {}
		obj = self.browse(cr,uid,ids)
		v ['state_canton'] = {
			'San Jose' : SJ_CANTON,
			'Heredia'  : (), 
		}[value](pField)
		
#		if pField == 'San Jose':
#			debug('asiiiiiiiiiiiiiiii')
#			v ['state_canton'] = SJ_CANTON
#			debug(pField)
#		elif pField == 'Cartago':
#	
#		elif pField == 'Alajuela':
#		
#		elif pField == 'Heredia':
#		elif pField == 'San Jose':
		return { 'value':v}
	def determine_district(self,cr,uid,ids,context=None):
		v = {}
		
		return {'value':v}
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

