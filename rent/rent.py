from osv import osv, fields
from tools import debug
import time
from dateutil import parser

class rent_canton(osv.osv):
	 _name = 'rent.canton'
	 _description = 'Canton for the State'
	 _columns = {
		'state_id'   : fields.many2one('res.country.state','Province',required=True),
		'name'       : fields.char('Canton Name', size=64, required=True),
		'code'       : fields.char('Canton Code', size=4,help = 'The canton code in 4 chars', required=True),
	 }
rent_canton()

class rent_canton_district(osv.osv):
	_name = 'rent.canton.district'
	_description = 'District located in the canton'
	_columns = {
		'canton_id'  : fields.many2one('rent.canton','Canton',required=True),
		'name'       : fields.char('Distric Name', size=64, required=True),
		'code'       : fields.char('Distric Code', size=4,help = 'The district code in 4 chars', required=True),
	}
rent_canton_district()


# Class used to specialize the res.partner.address, this one adds the attributes of
# canton, district and redefines the estate_id to province making it as a selection
class rent_location(osv.osv):
	_name = 'res.partner.address'
	_inherit = 'res.partner.address'

	_columns = {
		#'province_id '   : fields.selection(_get_province,'Province',size=16),
		#'canton_id'   : fields.selection(_get_canton, 'Canton'),
		'canton_id'   : fields.many2one('rent.canton', 'Canton', domain = "[('state_id','=',state_id)]"),
		'district_id' : fields.many2one('rent.canton.district','District', domain = "[('canton_id','=',canton_id)]"),
	}
rent_location()

#Class that inherits from res.partner allowing to record the 
#necesary data from the clients

class rent_client(osv.osv):
	_name = 'rent.client'
	_inherit = 'res.partner'
	_columns = {
		'client_birthdate' : fields.date('Birthdate',select=1,required=True),
		#'client_location'  : fields.one2many('rent.location','location_id','Location'),
		'client_canton'    : fields.related('address', 'canton_id', type='many2one', relation='rent.canton', string='Canton'),
		'client_district'  : fields.related('address', 'district_id', type='many2one', relation='rent.canton.district', string='District'),
	}
rent_client()


#Class that represents the estates owned by the user. 
#This class also uses the rent.location defined above
class rent_estate(osv.osv):
	_name = 'rent.estate'
	_rec_name = "estate_number"
	
	def _get_estate_vrm(self,cr,uid,ids,field_name,args,context=None):
		res = {}
		for estate_id in ids:
			obj_estate = self.pool.get('rent.estate').browse(cr,uid,estate_id)
			res[estate_id] = obj_estate.estate_value / obj_estate.estate_area
		return res
	
	def calculate_vrm(self,cr,uid,ids,context):
		res = {}
		self.pool.get('rent.estate').write(cr, uid, ids, {}, context)
		return { 'value' : res}
		
	_columns = {
		'estate_owner'    : fields.many2one('res.company','Owner',required=True),
		'estate_number'   : fields.char('# estate', size=10,required=True),
		'estate_value'    : fields.float('VRN Dynamic',required=True),
		'estate_area'     : fields.float('Area', required=True),
		'estate_vrn_per_sqr' : fields.function(_get_estate_vrm,type='float',method=True,string='VRN Din/M2'),#fields.float('VRN Din/M2',store=False, readonly=True),
		'estate_buildings': fields.one2many('rent.building','building_estate','Buildings'),
		'estate_location' : fields.many2one('res.partner.address','Location'),
		#'estate_province': fields.related('estate_address', 'estate_province', type='selection', string='Province'),
        #'estate_canton': fields.related('estate_address', 'estate_canton', type='selection', string='Canton'),
        #'estate_district': fields.related('estate_address', 'estate_district', type='selection', string='District'),
	}
rent_estate()

#Class building to represente a Real Estate, that is on any land previously define by the user
#this class contains the necesary data to determine the value for rent of the building
class rent_building(osv.osv):
	_name = 'rent.building'
	
	def _get_building_vrm(self,cr,uid,ids,field_name,args,context=None):
		res = {}
		for building_id in ids:
			obj_building = self.pool.get('rent.building').browse(cr,uid,building_id)
			res[building_id] = obj_building.building_value / obj_building.building_area
		return res
		
	_columns = {
		'building_capacity'          : fields.integer('Capacity',required=True),
		'building_date_construction' : fields.date('Construction Date', required=True),
		'building_elevator'          : fields.boolean('Elevadores',help='Select if the building has at least one elevator'),
		'building_elevators_number'  : fields.integer('Elvetators number',readonly=True,help='If checkbox of elevators is no selected this will be 0'),
		'building_stairs'            : fields.boolean('Stairs',help='Select if the building has at least one elevator'),
		'building_stairs_number'     : fields.integer('Stairs number',readonly=True,help='If checkbox of stairs is no selected this will be 0'),
		'name'                       : fields.char('Name', size=40,required=True),
		'building_value'             : fields.float('VRN Dynamic',required=True),
		'building_area'              : fields.float('Area',required=True),
		'building_estate'            : fields.many2one('rent.estate', 'estate'),
		'building_photo'             : fields.binary('Photo'),
		'building_floors'            : fields.one2many('rent.floor','floor_building','Floors'),
		'building_vrn_per_sqr'       : fields.function(_get_building_vrm,type='float',method=True,string='VRN Din/M2'),
	}
rent_building()

#Class that represents every single floor contained on the building, defined above
#All floors are differenced by the number starting from 0 (basement), then higher 
#the numbre then near to the top of the building is the floor.
class rent_floor(osv.osv):
	_name = 'rent.floor'
	_rec_name = 'floor_number'
	
	def _calculate_floor_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		valores = {}
		total = 0
		debug("CALCULO====================")
		debug(ids)
		for floor_id in ids:
			debug(floor_id)
			actual_rent = self.pool.get('rent.rent').search(cr,uid,['|',('rent_status','=','Valid'),('rent_status','=','Draft')])
			debug(actual_rent)
			locals_id = self.pool.get('rent.local.floor').search(cr,uid,[('local_rent','in',actual_rent),('local_floor_floor','=',floor_id)])
			debug(locals_id)
			for local in locals_id:
				obj_local = self.pool.get('rent.local.floor').browse(cr,uid,local)
				valores = obj_local._local_value(local,None,None)
				debug(valores)
				debug(local)
				total += valores[local]
				debug(total)
			
			#se obtienen los parqueos del piso asociados en otras rentas
			rent_ids = actual_rent.search(cr,uid,[('rent_is_parking','=','True')])
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_ids)
			for rent in obj_rent:
				obj_parking = rent.rent_rent_parking
				total += obj_parking._parking_value(obj_parking.id,None,None)[obj_parking.id]
			res[floor_id] = total
			total = 0
		return res
	
	_columns = {
		'floor_number'     : fields.integer('# Floor',required=True, help='Number of the floor in the building, starts from 0 (Basement)'),
		'floor_thickness'  : fields.float('Thickness'),
		'floor_durability' : fields.integer('Durability', help='Indicate the durability in years'),
		'floor_area'       : fields.float('Area',required=True),
		'floor_value'      : fields.function(_calculate_floor_value,type='float',method=True,string='Value',help='This value is calculated using the estate and building area and values'),
		'floor_acabado'    : fields.char('Acabado',size=64),
		'floor_local'      : fields.one2many('rent.floor.local','local_floor','Local'),
		'floor_parking'    : fields.one2many('rent.floor.parking','parking_floor','Parking'),
		'floor_building'   : fields.many2one('rent.building','Building'),
	}
rent_floor()

#Class representing the local, on every floor. This class has a relation 
#many2one with the floor 
#
class rent_floor_local(osv.osv):
	_name = 'rent.floor.local'
	_rec_name = 'local_number'
		
	def _get_building_local(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj_local = self.pool.get('rent.floor.local').browse(cr,uid,local_id)
			obj_floor = self.pool.get('rent.floor').browse(cr,uid,obj_local.local_floor)
			res[local_id] = obj_floor.floor_building
		return res
		
	_columns = {
		#'local_area'               : fields.function(_floor_area,type='float',method=True,string='VRN Dynamic'),
		'local_area'               : fields.float('VRN Dynamic',required=True),
		#'local_value'              : fields.float('Value',required=True),
		'local_number'             : fields.integer('# Local',required=True),
		'local_huella'             : fields.float('Huella',required=True),
		'local_water_meter_number' : fields.char('Water Meter',size=64), 
		'local_light_meter_number' : fields.char('Light Meter', size=64),
		#'local_sqrmeter_price'     : fields.function(_local_sqr_price,type='float',method=True,string='Sqr Meter Price'),
		'local_sqrmeter_price'     :  fields.float('Sqr Meter Price',required=True),
		'local_rented'             : fields.boolean('Rented',help='Check if the local is rented'),
		'local_floor'              : fields.many2one('rent.floor','# Floor'),
		'local_building'           : fields.function(_get_building_local,type='many2one',method=True,string='Building'),
	}
rent_floor_local()

#Class representing the parking, on floor. This class has a relation 
#many2one with the floor 
#
class rent_floor_parking(osv.osv):
	_name = 'rent.floor.parking'
	_rec_name = 'parking_number'
	
	def _parking_sqr_price(self,cr,uid,ids,field_name,args,context):
		res = {}
		for parking_id in ids:
			obj = self.pool.get('rent.floor.parking').browse(cr,uid,parking_id)
			obj_build = obj.parking_floor.floor_building
			res[parking_id] = obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
	
	def _parking_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		for parking_id in ids:
			obj = self.pool.get('rent.floor.parking').browse(cr,uid,parking_id)
			areas = obj._parking_area(parking_id,None,None)
			obj_build = obj.parking_floor.floor_building
			res[parking_id] = areas[parking_id] * obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
		
	def _parking_area(self,cr,uid,ids,field_name,args,context):
		res = {}
		for parking_id in ids:
			obj = self.pool.get('rent.floor.parking').browse(cr,uid,parking_id)
			res[parking_id] = obj.parking_large * obj.parking_width
		return res
		
	_columns = {
		'parking_area'            : fields.function(_parking_area,type='float',method=True,string='Area'),
		#'parking_area'            : fields.float('VRN Dynamic',required=True),
		#'parking_value'           : fields.float('Value',required=True),
		'parking_value'           : fields.function(_parking_value,type='float',method=True,string='Value'),
		'parking_number'          : fields.integer('# Parking',required=True),
		'parking_huella'          : fields.float('Huella',required=True),
		'parking_sqrmeter_price'  :  fields.function(_parking_sqr_price,type='float',method=True,string='Sqr Meter Value'),
		#'parking_sqrmeter_price'  :  fields.float('Sqr Meter Value',required=True),
		'parking_rented'          : fields.boolean('Rented',help='Checked if the local is rented',readonly=True),
		'parking_floor'           : fields.many2one('rent.floor','# Floor'),
		'parking_large'           : fields.float('Large Meters'),
		'parking_width'           : fields.float('Width Meters'),
	}
rent_floor_parking()


#Class to hold all the information that refences the rent
#value, dates, status and to control de transaction of the bussines
#
class rent_rent(osv.osv):
	_name = 'rent.rent'
	
	def _get_total_rent(self,cr,uid,ids,field_name,args,context):
		res = {}
		total = 0
		debug('+==================================')
		for rent_id in ids:
			debug(rent_id)
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_id)
			debug(obj_rent)
			if obj_rent.rent_is_local:
				debug("LOCALES")
				debug(obj_rent.rent_rent_local)
				for obj_local in obj_rent.rent_rent_local:
					total += obj_local._local_value(obj_local.id,None,None)[obj_local.id]
					debug(total)
			elif obj_rent.rent_is_parking:
				debug("PARQUEO")
				obj_parking = obj_rent.rent_rent_parking
				debug(obj_parking)
				total = obj_parking._parking_value(obj_parking.id,None,None)[obj_parking.id]
			else:
				debug("LOTES")
				debug(obj_rent.rent_rent_estate)
				obj_estado = obj_rent.rent_rent_estate
				total = obj_estado._get_estate_vrm(obj_estado.id,None,None)[obj_estado.id]
				debug(total)
				#for obj_estado in obj_rent.rent_rent_estate:
					#debug(obj_estado)
					#total += obj_estado._get_estate_vrm(obj_estado.id,None,None)[obj_estado.id]
			res[rent_id] = total
		return res
	def _calculate_years(self,cr,uid,ids,field_name,args,context):
		debug('+==================================')
		res = {}
		for rent_id in ids:
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_id)
			fin = parser.parse(obj_rent.rent_end_date)
			inicio = parser.parse(obj_rent.rent_start_date)
			debug(inicio)
			debug(fin)
			res[rent_id] = (fin.year - inicio.year)
			debug(res)
		return res
	def rent_valid(self,cr,uid,ids,context=None):
		debug('BOTON====================================')
		debug(ids)
		for rent_id in ids:
			self.pool.get('rent.rent').write(cr,uid,rent_id,{'rent_status':'Valid'})
		return True
	_columns = {
		'name'                  : fields.char('Reference',size=64),
		'rent_rent_client'      : fields.many2one('rent.client','Client'),
		'rent_end_date'         : fields.date('Ending Date'),
		'rent_ending_motif'     : fields.selection((('Desertion','Desertion'),('No Renovation','No Renovation'),('Eviction','Eviction')),'Ending Motif'),
		'rent_ending_motif_desc': fields.text('Ending Motif Description'),
		'rent_rise'             : fields.float('Rise'),
		'rent_type'             : fields.selection((('Contract','Contract'),('Adendum','Adendum'),('Renovation','Renovation')),'Type'),
		'rent_status'           : fields.selection((('Valid','Valid'),('Finished','Finished'),('Draft','Draft')),'Status'),
		'rent_start_date'       : fields.date('Starting Date'),
		'rent_total'            : fields.function(_get_total_rent,type='float',method=True,string='Total Paid'),
		'rent_rent_local'       : fields.one2many('rent.local.floor','local_rent','Local'),
		'rent_rent_parking'     : fields.many2one('rent.floor.parking','Parking'),
		'rent_rent_estate'      : fields.many2one('rent.estate','Estate'),
		'rent_is_local'         : fields.boolean('Locals',help='Check if you want to calculate a rent for locals'),
		'rent_is_parking'       : fields.boolean('Parking',help='Check if you want to calculate a rent for locals'),
		'rent_is_estate'        : fields.boolean('Estates',help='Check if you want to calculate a rent for locals'),
		'rent_years'            : fields.function(_calculate_years,type='integer',method=True,string = 'Years' ,help='Check if you want to calculate a rent for locals'),
	}
rent_rent()

class rent_local_floor(osv.osv):
	_name = 'rent.local.floor'
	
	def _local_sqr_price(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_id)
			areas = obj._local_floor_area(local_id,'local_local_floor',None)
			obj_build = obj.local_floor_floor.floor_building
			res[local_id] = obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
	
	def _local_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_id)
			areas = obj._local_floor_area(local_id,'local_local_floor',None)
			obj_build = obj.local_floor_floor.floor_building
			res[local_id] = areas[local_id] * obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
		
	def _local_floor_area(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_floor_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_floor_id)
			res[local_floor_id] = obj.local_floor_width * obj.local_floor_large
		return res
	
	_columns = {
		'name'                 : fields.char('Reference',size=64,help='Indicate a representative reference for the asociation'),
		'local_floor_width'    : fields.float('Width', required=True),
		'local_floor_large'    : fields.float('Large', required=True),
		'local_floor_floor'    : fields.many2one('rent.floor','Level',help='Represents the floor on witch its located the local'),
		'local_local_floor'    : fields.many2one('rent.floor.local','Local#',help='Represents the floor on witch its located the local'),
		'local_rent'           : fields.many2one('rent.rent','Alquiler'),
		'local_floor_area'     : fields.function(_local_floor_area,type='float',method=True,string='Area M2'),
		'local_sqrmeter_price' : fields.function(_local_sqr_price,type='float',method=True,string='Sqr Meter Price'),
		'local_floor_value'    : fields.function(_local_value,type='float',method=True,string='Total Value'),
	}
rent_local_floor()

#
#
#
class rent_contract(osv.osv):
	_name = 'rent.contract'
	_columns = {
		'name'             : fields.char('Reference', size=64),
		'contract_rent'    : fields.many2one('rent.rent','Rent Reference'),
		'contract_clauses' : fields.one2many('rent.contract.clause.rel','rent_contract_id','Clausulas'),
		#'contract_clauses' : fields.many2many('rent.contract.clause','rent_contract_clause_rel','name','clause_code','Clausulas'),
		'contract_design'  : fields.char('Design',size=64),
	}
rent_contract()


#Class that holds all the clauses for the contracts
#this class is used to create a custom contract
#it simulates a sintaxys analizer to subtitute codes with the corresponding clause
class rent_contract_clause(osv.osv):
	_name = 'rent.contract.clause'
	_rec_name = 'clause_code'
	_columns = {
		'clause_code'     : fields.char('Reference',size=64,required=True,help='Reference code for the clause, used to create custom contracts'),
		'clause_subject'  : fields.char('Subject',size=64,required=True),
		'clause_body'     : fields.text('Body',required=True),
		#'clause_contract' : fields.many2many('rent.contract','rent_contract_clause','id','id','Contracts'),
	}
rent_contract_clause()


class rent_contract_clause_rel(osv.osv):
	_name = 'rent.contract.clause.rel'
	_rec_name = 'rent_contract_id'
	_columns = {
		'rent_contract_id' : fields.many2one('rent.contract','Contract Reference'),
		'rent_contract_clause_id' : fields.many2one('rent.contract.clause','Contract Reference'),
		'sequence'         : fields.integer('Sequence'),
	}
rent_contract_clause_rel()
