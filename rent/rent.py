from osv import osv, fields
from tools import debug
import time
import pooler
from dateutil import parser
from datetime import date
from datetime import timedelta
import calendar
from tools.translate import _

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
		'canton_id'   : fields.many2one('rent.canton', 'Canton', domain = "[('state_id','=',state_id)]"),
		'district_id' : fields.many2one('rent.canton.district','District', domain = "[('canton_id','=',canton_id)]"),
	}
rent_location()

#Class that inherits from res.partner allowing to record the 
#necesary data from the clients

class rent_client(osv.osv):
	_name = 'res.partner'
	_inherit = 'res.partner'
	_columns = {
		#'client_birthdate' : fields.date('Birthdate',select=1,required=True),
		'client_canton'    : fields.related('address', 'canton_id', type='many2one', relation='rent.canton', string='Canton'),
		'client_district'  : fields.related('address', 'district_id', type='many2one', relation='rent.canton.district', string='District'),
	}
rent_client()


#Class that represents the estates owned by the user. 
#This class also uses the rent.location defined above
class rent_estate(osv.osv):
	_name = 'rent.estate'
	_rec_name = "estate_number"
	
	def write (self, cr, uid,ids,vals,context=None):
		#Check for the area before saving the changes
		for obj_estate in self.browse(cr,uid,ids):
			if obj_estate.estate_area == 0:
				raise osv.except_osv('Wrong value!', 'The area for the estate has to bee greater than 0')
		return super(rent_estate,self).write(cr,uid,ids,vals,context)
	def create(self, cr, uid,vals, context=None):
		#Check for the area before creating the object
		if vals['estate_area'] == 0:
			raise osv.except_osv('Wrong value!', 'The area for the estate has to bee greater than 0')
		return super(rent_estate,self).create(cr,uid,vals,context)
	
	def _get_estate_vrm(self,cr,uid,ids,field_name,args,context=None):
		res = {}
		for obj_estate in self.pool.get('rent.estate').browse(cr,uid,ids):
			if obj_estate.estate_area == 0:
				raise osv.except_osv('Wrong value!', 'The area for the estate has to bee greater than 0')
			else:
				res[obj_estate.id] = obj_estate.estate_value / (obj_estate.estate_area == 0 and 1 or obj_estate.estate_area)
		return res
	
	def calculate_vrm(self,cr,uid,ids,context):
		res = {}
		self.pool.get('rent.estate').write(cr, uid, ids, {}, context)
		return { 'value' : res}
	def _determine_rented(self,cr,uid,ids,field_name,args,context):
		res = {}
		for estate_id in ids:
			res[estate_id] =  False
			debug(ids)
			rent_ids = self.pool.get('rent.rent').search(cr,uid,[('state','=','active'),('rent_related_real','=','estate'),('rent_rent_local_id','=',estate_id)])
			if rent_ids:
				res[estate_id] =  True
		debug(res)
		return res
	_columns = {
		'estate_owner_id'     : fields.many2one('res.company','Owner',required=True),
		'estate_number'       : fields.char('# estate', size=20,required=True),
		'estate_value'        : fields.float('VRN Dynamic',required=True),
		'estate_area'         : fields.float('Area', required=True),
		'estate_vrn_per_sqr'  : fields.function(_get_estate_vrm,type='float',method=True,string='VRN Din/M2'),#fields.float('VRN Din/M2',store=False, readonly=True),
		'estate_buildings_ids': fields.one2many('rent.building','building_estate_id','Buildings'),
		'estate_location_id'  : fields.many2one('res.partner.address','Location'),
		'estate_account_id'   : fields.many2one('account.account', 'Cuenta'),
		'estate_rented'       : fields.function(_determine_rented,type='boolean',method=True,string='Rented',help='Checked if the local is rented', store=True),
	}
	_sql_constraints = [
		('estate_area_gt_zero', 'CHECK (estate_area!=0)', 'The area for the estate cannot be 0!'),
		('estate_number_key','UNIQUE (estate_number)','You can not have two estates with the same number!'),
	]
rent_estate()

#Class building to represente a Real Estate, that is on any land previously define by the user
#this class contains the necesary data to determine the value for rent of the building
class rent_building(osv.osv):
	_name = 'rent.building'
	
	def write (self, cr, uid,ids,vals,context=None):
		#Check for the area before saving the changes
		for obj_building in self.browse(cr,uid,ids):
			if obj_building.building_area == 0:
				raise osv.except_osv('Wrong value!', 'The area for the building has to bee greater than 0')
		return super(rent_building,self).write(cr,uid,ids,vals,context)
	def create(self, cr, uid,vals, context=None):
		#Check for the area before creating the object
		if vals['building_area'] == 0:
			raise osv.except_osv('Wrong value!', 'The area for the building has to bee greater than 0')
		return super(rent_building,self).create(cr,uid,vals,context)
	
	def _get_building_vrm(self,cr,uid,ids,field_name,args,context=None):
		#This method calculates the vrn acording to the value an area of the building
		res = {}
		for building_id in ids:
			obj_building = self.pool.get('rent.building').browse(cr,uid,building_id)
			try:
				res[building_id] = obj_building.building_value / obj_building.building_area
			except:
				res[building_id] = 0
		return res
		
	_columns = {
		'building_capacity'          : fields.integer('Capacity'),
		'building_date_construction' : fields.date('Construction Date'),
		'building_elevator'          : fields.boolean('Elevadores',help='Select if the building has at least one elevator'),
		'building_elevators_number'  : fields.integer('Elvetators number',readonly=True,help='If checkbox of elevators is no selected this will be 0'),
		'building_stairs'            : fields.boolean('Stairs',help='Select if the building has at least one elevator'),
		'building_stairs_number'     : fields.integer('Stairs number',readonly=True,help='If checkbox of stairs is no selected this will be 0'),
		'name'                       : fields.char('Name', size=40,required=True),
		'building_value'             : fields.float('VRN Dynamic',required=True),
		'building_area'              : fields.float('Area',required=True),
		'building_estate_id'         : fields.many2one('rent.estate', 'estate',required=True),
		'building_photo'             : fields.binary('Photo'),
		'building_gallery_photo'     : fields.char('Gallery of Photos', size=64),
		'building_floors_ids'        : fields.one2many('rent.floor','floor_building_id','Floors'),
		'building_vrn_per_sqr'       : fields.function(_get_building_vrm,type='float',method=True,string='VRN Din/M2'),
		'building_code'              : fields.char('Code', size=4, required=True),
		'building_asset_id'          : fields.many2one('account.asset.asset','Asset'),
		'building_company_id'        : fields.many2one('res.company','Company',required=True),
	}
	_sql_constraints = [
		('building_area_gt_zero', 'CHECK (building_area!=0)', 'The area for the building cannot be 0!'),
		('building_code','UNIQUE (building_code)','You can not have two buildings with the same code!'),
	]
rent_building()

#Class that represents every single floor contained on the building, defined above
#All floors are differenced by the number starting from 0 (basement), then higher 
#the numbre then near to the top of the building is the floor.
class rent_floor(osv.osv):
	_name = 'rent.floor'
	_rec_name = 'floor_number'
	
	def write (self, cr, uid,ids,vals,context=None):
		#Check for the area before saving the changes
		for obj_floor in self.browse(cr,uid,ids):
			if obj_floor.floor_area == 0:
				raise osv.except_osv('Wrong value!', 'The area for the floor has to bee greater than 0')
			if vals and vals['floor_number']:
				obj_build = obj_floor.floor_building_id
				for obj_f in obj_build.building_floors_ids:
					if obj_f.floor_number.upper() == vals['floor_number'].upper() and obj_f.id  != obj_floor.id:
						raise osv.except_osv('Wrong value!', 'The number for the floor at the same building cannot be repeated')
		return super(rent_floor,self).write(cr,uid,ids,vals,context)
	def create(self, cr, uid,vals, context=None):
		#Check for the area before creating the object
		if vals['floor_area'] == 0:
			raise osv.except_osv('Wrong value!', 'The area for the floor has to bee greater than 0')
		if vals['floor_number']:
				obj_build = self.pool.get('rent.building').browse(cr,uid,vals['floor_building_id'])
				for obj_f in obj_build.building_floors_ids:
					if obj_f.floor_number.upper() == vals['floor_number'].upper():
						raise osv.except_osv('Wrong value!', 'The number for the floor at the same building cannot be repeated')
		return super(rent_floor,self).create(cr,uid,vals,context)
	
	def _calculate_floor_value(self,cr,uid,ids,field_name,args,context):
		#This method takes al the active rents for the floor and calculates the value according to 
		#the value of the locals,parking, building and estate related to it
		res = {}
		valores = {}
		total = 0
		for floor_id in ids:
			actual_rent = self.pool.get('rent.rent').search(cr,uid,['|',('state','=','active'),('state','=','draft'),('rent_related_real','=','local')])
			for obj_rent in self.pool.get('rent.rent').browse(cr,uid,actual_rent):
				obj_local = obj_rent.rent_rent_local_id
				local_floor_ids = self.pool.get('rent.local.floor').search(cr,uid,[('local_local_floor_id','=',obj_local.id),('local_floor_floor_id','=',floor_id)])
				for local in self.pool.get('rent.local.floor').browse(cr,uid,local_floor_ids):
					valores = local._local_value(local.id,None,None)
					total += valores[local.id]
			
			#This part look for the parking on rents associated to the floor
			rent_ids = self.pool.get('rent.rent').search(cr,uid,['|',('state','=','active'),('state','=','draft'),('rent_related_real','=','parking')])
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_ids)
			for rent in obj_rent:
				obj_parking = rent.rent_rent_parking_id
				if (obj_parking.parking_floor_id.id == floor_id):
					total += obj_parking._parking_value(obj_parking.id,None,None)[obj_parking.id]
			res[floor_id] = total
			total = 0
		return res
	
	def _get_fullname(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_floor in self.pool.get('rent.floor').browse(cr,uid,ids):
			building_code = obj_floor.floor_building_id.building_code
			res[obj_floor.id] = building_code + '-' + obj_floor.floor_number
		debug(res)
		return res
	 
	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['complete_name'], context=context)
		res = []
		for record in reads:
			name = record['complete_name']
			res.append((record['id'], name))
		return res

	_columns = {
		'floor_number'     : fields.char('# Floor',size=16,required=True, help='Number of the floor in the building, starts from 0 (Basement)'),
		'floor_thickness'  : fields.float('Thickness'),
		'floor_durability' : fields.integer('Durability', help='Indicate the durability in years'),
		'floor_area'       : fields.float('Area',required=True),
		'floor_value'      : fields.function(_calculate_floor_value,type='float',method=True,string='Value',help='This value is calculated using the estate and building area and values'),
		'floor_acabado'    : fields.char('Acabado',size=64),
		'floor_parking_ids'    : fields.one2many('rent.floor.parking','parking_floor_id','Parking'),
		'floor_building_id'   : fields.many2one('rent.building','Building'),
		'complete_name'    : fields.function(_get_fullname,type='char',method=True,string='Name',help='This name uses the code of the building and the floor name'),
	}
	_sql_constraints = [
		('floor_area_gt_zero', 'CHECK (floor_area!=0)', 'The area for the floor cannot be 0!'),
		('floor_building_number_key','UNIQUE(floor_number,floor_building_id)','You can not have two floors with the same number at the same building!'),
	]
rent_floor()

#Class representing the local, on every floor. This class has a relation 
#many2one with the floor 
class rent_floor_local(osv.osv):
	_name = 'rent.floor.local'
	_rec_name = 'local_number'
	
	def write (self, cr, uid,ids,vals,context=None):
		#Check for the area before saving the changes
		for obj_local in self.browse(cr,uid,ids):
			if obj_local.local_huella == 0:
				raise osv.except_osv('Wrong value!', 'The huella for the local has to bee greater than 0')
		return super(rent_floor_local,self).write(cr,uid,ids,vals,context)
	def create(self, cr, uid,vals, context=None):
		#Check for the area before creating the object
		if vals['local_huella'] == 0:
			raise osv.except_osv('Wrong value!', 'The huella for the local has to bee greater than 0')
		return super(rent_floor_local,self).create(cr,uid,vals,context)
	
	def _get_building_local(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			local = self.pool.get('rent.local.floor').search(cr,uid,[('local_local_floor_id','=',local_id)])
			res[local_id] = False
			for lids in local:
				obj_local = self.pool.get('rent.local.floor').browse(cr,uid,lids)
				res[local_id] = obj_local.local_floor_floor_id.floor_building_id.id
		return res
	
	def _determine_rented(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			res[local_id] =  False
			rent_ids = self.pool.get('rent.rent').search(cr,uid,[('state','=','active'),('rent_related_real','=','local'),('rent_rent_local_id','=',local_id)])
			if rent_ids:
				res[local_id] =  True
		return res
	def _local_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		total = 0
		for local in self.pool.get('rent.floor.local').browse(cr,uid,ids):
			for obj_local_floor in local.local_local_by_floor_ids:
				total += obj_local_floor._local_value(obj_local_floor.id,None,None)[obj_local_floor.id]
			res[local.id] = total
			total = 0
		return res

	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['local_number','local_building'], context=context)
		res = []
		for record in reads:
			if record['local_number'] and record['local_building'] and record['local_building'][1]:
				name = 'Local #' + str(record['local_number']) + ' , ' +  record['local_building'][1]
				res.append((record['id'], name))
		return res
	
	#This method takes the area of every record of local_by_floor and calculates the total area
	def _local_area(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_local in self.pool.get('rent.floor.local').browse(cr,uid,ids):
			total = 0
			for obj_local_floor in obj_local.local_local_by_floor_ids:
				total += obj_local_floor.local_floor_area
			res[obj_local.id] = total
		return res
	
	_columns = {
		'local_area'               : fields.function(_local_area,type='float',method=True,string='VRN Dynamic'),
		'local_number'             : fields.char('# Local',required=True, size=64),
		'local_huella'             : fields.float('Huella',required=True),
		'local_water_meter_number' : fields.char('Water Meter',size=64), 
		'local_light_meter_number' : fields.char('Electric Meter', size=64),
		'local_rented'             : fields.function(_determine_rented,type='boolean',method=True,string='Rented',help='Check if the local is rented',store=True),
		'local_local_by_floor_ids' : fields.one2many('rent.local.floor','local_local_floor_id','Local floors'),
		'local_building'           : fields.function(_get_building_local,type='many2one',obj='rent.building',method=True,string='Building'),
		'local_gallery_photo'      : fields.char('Photo Gallery', size=64),
		'local_photo'              : fields.binary('Main photo'),
		'local_rise_historic_ids'  : fields.one2many('rent.rent.anual.value','anual_value_local_ids','Historic', readonly=True),
		'local_notes'              : fields.text('Notes'),
	}
	_sql_constraints = [
		('local_huella_gt_zero', 'CHECK (local_huella!=0)', 'The area for the floor cannot be 0!'),
	]
rent_floor_local()

class rent_local_floor(osv.osv):
	_name = 'rent.local.floor'
	
	def write (self, cr, uid,ids,vals,context=None):
		#Check for the building and the floor so it can't be at diferent places before saving the changes
		if vals['local_floor_floor_id']:
			for obj_local_floor in self.browse(cr,uid,ids):
				for obj_local_floor_check in obj_local_floor.local_local_floor_id.local_local_by_floor_ids:
					current_floor = self.pool.get('rent.floor').browse(cr,uid,vals['local_floor_floor_id'])
					if obj_local_floor_check.local_floor_floor_id.floor_building_id.id != current_floor.floor_building_id.id:
						raise osv.except_osv('Wrong value!', 'The same local can not be on diferent buildings')
						break
		return super(rent_local_floor,self).write(cr,uid,ids,vals,context)
	def create(self, cr, uid,vals, context=None):
		#Check for the building and the floor so it can't be at diferent places before creating the object
		locations_ids = self.search(cr,uid,[('local_local_floor_id','=',vals['local_local_floor_id'])])
		debug(locations_ids)
		current_floor = self.pool.get('rent.floor').browse(cr,uid,vals['local_floor_floor_id'])
		debug(current_floor)
		for obj_local_floor in self.browse(cr,uid,locations_ids):
			debug(obj_local_floor)
			debug(obj_local_floor.local_floor_floor_id.floor_building_id.id)
			debug(current_floor.floor_building_id.id)
			if obj_local_floor.local_floor_floor_id.floor_building_id.id != current_floor.floor_building_id.id:
				raise osv.except_osv('Wrong value!', 'The same local can not be on diferent buildings')
		return super(rent_local_floor,self).create(cr,uid,vals,context)
	
	def _local_sqr_price(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_id)
			obj_build = obj.local_floor_floor_id.floor_building_id
			res[local_id] = obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
	
	def _local_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_id)
			obj_build = obj.local_floor_floor_id.floor_building_id
			res[local_id] = obj.local_floor_area * obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
	
	def onchange_floor(self,cr,uid,ids,floor_id):
		res = {}
		if floor_id:
			obj_floor = self.pool.get('rent.floor').browse(cr,uid,floor_id)
			if obj_floor:
				res['local_floor_building'] = obj_floor.floor_building_id.id
		return {'value' : res}
	_columns = {
		'local_floor_front'     : fields.float('Front', required=True),
		'local_floor_side'      : fields.float('Side', required=True),
		'local_floor_floor_id'  : fields.many2one('rent.floor','Level',help='Represents the floor on witch its located the local',required=True),
		'local_local_floor_id'  : fields.many2one('rent.floor.local','Local#',help='Represents the floor on witch its located the local'),
		'local_floor_area'      : fields.float('Area M2',required=True),
		'local_sqrmeter_price'  : fields.function(_local_sqr_price,type='float',method=True,string='Sqr Meter Price'),
		'local_floor_value'     : fields.function(_local_value,type='float',method=True,string='Total Value'),
		'local_floor_building'  : fields.related('local_floor_floor_id','floor_building_id',type='many2one',relation='rent.building',string='Building', readonly=True, store=False),
	} 
	_sql_constraints = [
		('local_floor_area_gt_zero', 'CHECK (local_floor_area!=0)', 'The area for the local at this floor cannot be 0!'),
		('local_floor_front_gt_zero', 'CHECK (local_floor_front!=0)', 'The front for the local cannot be 0!'),
		('local_floor_side_gt_zero', 'CHECK (local_floor_side!=0)', 'The side for the local cannot be 0!'),
		('local_floor_location_key','UNIQUE (local_floor_floor_id,local_local_floor_id)','You can not repeat the local at the same floor!'),
	]
rent_local_floor()

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
			obj_build = obj.parking_floor_id.floor_building_id
			res[parking_id] = obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
	
	def _parking_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		for parking_id in ids:
			obj = self.pool.get('rent.floor.parking').browse(cr,uid,parking_id)
			areas = obj._parking_area(parking_id,None,None)
			obj_build = obj.parking_floor_id.floor_building_id
			res[parking_id] = areas[parking_id] * obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
		
	def _parking_area(self,cr,uid,ids,field_name,args,context):
		res = {}
		for parking_id in ids:
			obj = self.pool.get('rent.floor.parking').browse(cr,uid,parking_id)
			res[parking_id] = obj.parking_large * obj.parking_width
		return res
	
	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['parking_number','parking_floor_id'], context=context)
		res = []
		debug('NOMBREPARKEO+==================================')
		for record in reads:
			debug(record)
			debug(record['parking_floor_id'][1])
			name = 'Parking #' + str(record['parking_number']) + ' , ' +  record['parking_floor_id'][1]
		#	for subrecord in subreads 
		#		name += ', ' + subrecord['local_floor_building']
			res.append((record['id'], name))
		return res
	
	def _determine_rented(self,cr,uid,ids,field_name,args,context):
		res = {}
		debug('Renta+==================================')
		for parking_id in ids:
			res[parking_id] =  False
			debug(ids)
			rent_ids = self.pool.get('rent.rent').search(cr,uid,[('state','=','active'),('rent_related_real','=','parking'),('rent_rent_parking_id','=',parking_id)])
			if rent_ids:
				res[parking_id] =  True
		debug(res)
		return res
	def onchange_floor(self,cr,uid,ids,floor_id):
		res = {}
		debug("+============================")
		obj_floor = self.pool.get('rent.floor').browse(cr,uid,floor_id)
		debug(obj_floor)
		res['parking_floor_building'] = obj_floor.floor_building_id.id
		debug(res)
		return {'value' : res}
		
	_columns = {
		'parking_area'            : fields.function(_parking_area,type='float',method=True,string='Area'),
		'parking_value'           : fields.function(_parking_value,type='float',method=True,string='Value'),
		'parking_number'          : fields.integer('# Parking',required=True),
		'parking_huella'          : fields.float('Huella',required=True),
		'parking_sqrmeter_price'  : fields.function(_parking_sqr_price,type='float',method=True,string='Sqr Meter Value'),
		'parking_rented'          : fields.function(_determine_rented,type='boolean',method=True,string='Rented',help='Checked if the parking is rented'),
		'parking_floor_id'        : fields.many2one('rent.floor','# Floor',required=True),
		'parking_large'           : fields.float('Large Meters'),
		'parking_width'           : fields.float('Width Meters'),
		'parking_floor_building'  : fields.related('parking_floor_id','floor_building_id',type='many2one',relation='rent.building',string='Building', readonly=True, store=False),
	}
	_sql_constraints = [
		('parking_huella_gt_zero', 'CHECK (parking_area!=0)', 'The huella for the parking cannot be 0!'),
		('parking_large_gt_zero', 'CHECK (parking_large!=0)', 'The large for the parking cannot be 0!'),
		('parking_width_gt_zero', 'CHECK (parking_width!=0)', 'The width for the parking cannot be 0!'),
		('local_floor_side_gt_zero', 'CHECK (local_floor_side!=0)', 'The side for the local cannot be 0!'),
		('parking_number_key','UNIQUE (parking_number,parking_floor_id)','You can not repeat the parking number at the same floor!'),
	]
rent_floor_parking()


#Class to hold all the information that refences the rent
#value, dates, status and to control de transaction of the bussines
#
class rent_rent(osv.osv):
	_name = 'rent.rent'
	
	def onchange_estimations(self,cr,uid,ids,field):
		res = {}
		debug("==========ESTIMACIONES====")
		debug(field)
		obj_sorted = sorted(field,key=lambda estimate: estimate.estimate_performance,reverse=True)
		priority = 1
		for obj_record in obj_sorted:
			vals = {}
			if obj_record.estimate_state != 'final':
				if priority == 1:
					vals['estimate_state'] = 'recommend'
				elif priority == 2:
					vals['estimate_state'] = 'min'
				else:
					vals['estimate_state'] = 'norec'
				priority += 1
			debug(vals)
			obj_record.write(vals)
		return True
		
	def _get_total_area(self,cr,uid,ids,fields_name,args,context):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			if obj_rent.rent_related_real == 'local':
				total = obj_rent.rent_rent_local_id.local_area
			elif obj_rent.rent_related_real == 'parking':
				total = obj_rent.rent_rent_parking_id.parking_area
			else:
				total = obj_rent.rent_rent_estate_id.estate_area
			res[obj_rent.id] = total
		return res
		
	def _get_currency(self, cr, uid, context=None):
		user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid], context=context)[0]
		if user.company_id:
			return user.company_id.currency_id.id
		return pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('rate','=', 1.0)])[0]
	
	def _get_currency_eqv(self, cr, uid, context=None):
		return pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('rate','=', 1.0)])[0]
		
	def _get_total_rent(self,cr,uid,ids,field_name,args,context):
		res = {}
		total = 0
		for obj_rent in self.browse(cr,uid,ids):
			if obj_rent.rent_related_real == 'local':
				obj_local = obj_rent.rent_rent_local_id
				total = obj_local._local_value(obj_local.id,None,None)[obj_local.id]
			elif obj_rent.rent_related_real == 'parking':
				obj_parking = obj_rent.rent_rent_parking_id
				total = obj_parking._parking_value(obj_parking.id,None,None)[obj_parking.id]
			else:
				obj_estado = obj_rent.rent_rent_estate_id
				total = obj_estado._get_estate_vrm(obj_estado.id,None,None)[obj_estado.id]
			
			obj_client = obj_rent.rent_rent_client_id
			company_currency = (obj_client.company_id and obj_client.company_id.currency_id or self._get_currency(cr,uid,context))
			
			to_exchange = {
				'obj_rent' : obj_rent,
				'vals'     : [('rent_total',total),
				],
				'from_currency' : company_currency,
				'to_currency'   : obj_rent.currency_id,
			}
			
			exchanged = self._calculate_exchange(cr,uid,ids,to_exchange)
			
			total = exchanged['rent_total']
			to_exchange = {
				'obj_rent' : obj_rent,
				'vals'     : [('rent_total_us',total),
				],
				'from_currency' : obj_rent.currency_id,
				'to_currency'   : obj_rent.eqv_currency_id,
			}
			exchanged = self._calculate_exchange(cr,uid,ids,to_exchange)
			total_vals = {}
			total_vals['rent_total'] = total
			total_vals['rent_total_us'] = exchanged['rent_total_us']
			res[ obj_rent.id] = total_vals
		return res
		
	def _calculate_years(self,cr,uid,ids,field_name,args,context):
		res = {}
		for rent_id in ids:
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_id)
			if (obj_rent.rent_end_date and  obj_rent.rent_start_date):
				fin = parser.parse(obj_rent.rent_end_date)
				inicio = parser.parse(obj_rent.rent_start_date)
				res[rent_id] = (fin.year - inicio.year)
		return res
	
	def copy (cr, uid, id, default=None, context=None):
		default.update({
			'rent_modif' : [],
			'rent_estimates_ids' : [],
			'rent_historic_ids' : [],
			'rent_invoice_ids' : [],
			'rent_main_estimates_ids' : [],
			'rent_historic_ids' : [],
			'rent_main_invoice_ids' : [],
			'state'      : 'draft',
		})
		return super(rent_rent, self).copy(cr, uid, id, default=default, context=context)
		
	def create(self,cr,uid, vals,context=None):
		rent_id = super(rent_rent,self).create(cr,uid,vals,context)
		obj_rent = self.browse(cr,uid,rent_id)
		return obj_rent.id
	
	def default_get(self,cr,uid,fields_list,context=None):
		debug ('DEFAULT_GET')
		debug (fields_list)
		res = {
				'name'                : name,
				'rent_rent_client_id' : rent_rent_client_id,
				'rent_end_date'       : rent_end_date,
				'rent_rise'           : rent_rise,
				'rent_amount_base'    : rent_amount_base,
				'rent_type'           : 'Adendum',
				'rent_start_date'     : rent_start_date,
				'rent_rent_local_id'  : rent_rent_local_id,
				'rent_rent_parking_id': rent_rent_parking_id,
				'rent_rent_estate_id' : rent_rent_estate_id,
				'rent_related_real'   : rent_related_real,
				'currency_id'         : currency_id,
				'eqv_currency_id'     : eqv_currency_id,
				'rent_invoiced_day'   : rent_invoiced_day,
				'rent_grace_period'   :rent_grace_period,
				'rent_rent_account_id': rent_rent_account_id,
				'rent_rent_acc_int_id': rent_rent_acc_int_id,
				'rent_main_inc'       : rent_main_inc,
				}
		return {}
		
	def write(self, cr, uid, ids, vals, context=None):
		obj_rent = self.pool.get('rent.rent').browse(cr,uid,ids)[0]
		if 'rent_related_real' in vals:			
			if (obj_rent.rent_related_real != vals['rent_related_real']):
				real_type = vals['rent_related_real'] 
				if real_type == 'local' or real_type == 'parking':
					vals['rent_rent_estate_id'] = False
				if real_type == 'local' or real_type == 'estate':
					vals['rent_rent_parking_id'] = False
				if real_type == 'parking' or real_type == 'estate':
					vals['rent_rent_local_id'] = False		
		super(rent_rent, self).write(cr, uid, ids, vals, context=context)
		if 'rent_estimates_ids' in vals:
			obj_rent.onchange_estimations(obj_rent.rent_estimates_ids)
		#if 'rent_amount_base' in vals: 
		#	self.register_historic(cr,uid,obj_rent)
		return True
		
	def register_historic(self,cr,uid,obj_rent):
		debug('HISTORIC+===================')
		#obj_rent = self.browse(cr,uid,ids)[0]
		debug(obj_rent)
		if obj_rent:
			vals = {}
			is_registrated = False
			current_date = parser.parse(obj_rent.rent_start_date).date()
			current_date = current_date.replace(year=date.today().year)
			for obj_historic in obj_rent.rent_historic_ids:
				debug(current_date.isoformat())
				debug(obj_historic.anual_value_date)
				if obj_historic.anual_value_date == current_date.isoformat():
					is_registrated = True
					match_historic = obj_historic
					break
			#We need to update the amount_base of the rent, so we ca
			#charge the next part with the rate included
			percentaje = obj_rent.rent_rise
			prev_value = obj_rent.rent_amount_base
			years_val = obj_rent.rent_amount_base * (1 + float(percentaje) / 100)
			#obj_rent.write({'rent_amount_base' : years_val})
			vals['rent_amount_base'] = years_val
			if obj_rent.rent_related_real == 'local':
				vals['anual_value_local_ids'] = obj_rent.rent_rent_local_id.id
			if not is_registrated:
				vals['rent_historic_ids'] = [(0,0,{'anual_value_rent_id':obj_rent.id,'anual_value_value':years_val,'anual_value_prev_value' : prev_value,'anual_value_rate' : obj_rent.rent_rise, 'anual_value_date' : current_date, 'anual_value_type' : 'rent', 'anual_value_local_ids':vals['anual_value_local_ids']})]
			else:
				vals['rent_historic_ids'] = [(1,match_historic.id,{'anual_value_value':obj_rent.rent_amount_base,'anual_value_rate' : obj_rent.rent_rise})]
			debug(vals)
			obj_rent.write(vals)
		return True
	
	def register_main_historic(self,cr,uid,obj_rent):
		debug('HISTORIC MAIN+===================')
		#obj_rent = self.browse(cr,uid,ids)[0]
		debug(obj_rent)
		if obj_rent:
			vals = {}
			is_registrated = False
			current_date = parser.parse(obj_rent.rent_main_start_date).date()
			current_date = current_date.replace(year=date.today().year)
			for obj_historic in obj_rent.rent_main_historic_ids:
				debug(current_date.isoformat())
				debug(obj_historic.anual_value_date)
				if obj_historic.anual_value_date == current_date.isoformat():
					is_registrated = True
					match_historic = obj_historic
					break
			#We need to update the amount_base of the rent, so we ca
			#charge the next part with the rate included
			amount_base = obj_rent.rent_main_amount_base
			rise = obj_rent.rent_main_rise
			percentaje = rise
			prev_value = amount_base
			years_val = amount_base * (1 + float(percentaje) / 100)
			#obj_rent.write({'rent_amount_base' : years_val})
			vals['rent_main_amount_base'] = years_val
			if obj_rent.rent_related_real == 'local':
				vals['anual_value_local_ids'] = obj_rent.rent_rent_local_id.id
			if not is_registrated:
				vals['rent_main_historic_ids'] = [(0,0,{'anual_value_rent_id':obj_rent.id,'anual_value_value':years_val,'anual_value_prev_value' : prev_value,'anual_value_rate' : rise, 'anual_value_date' : current_date, 'anual_value_type' : 'main','anual_value_local_ids':vals['anual_value_local_ids']})]
			else:
				vals['rent_main_historic_ids'] = [(1,match_historic.id,{'anual_value_value':amount_base,'anual_value_rate' : rise})]
			debug(vals)
			obj_rent.write(vals)
		return True
	def _performance_per_sqr(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			amounts_val = {}
			valor = obj_rent._get_total_area(obj_rent.id,None,None)[obj_rent.id]
			amounts_val['rent_amount_per_sqr'] = (obj_rent.rent_amount_base / valor) 
			
			to_exchange = {
				'obj_rent' : obj_rent,
				'vals'     : [('rent_amountd_per_sqr',amounts_val['rent_amount_per_sqr']),
				],
				'from_currency' : obj_rent.currency_id,
				'to_currency'   : obj_rent.eqv_currency_id,
			}
			
			exchanged = self._calculate_exchange(cr,uid,ids,to_exchange)
			amounts_val['rent_amountd_per_sqr'] = exchanged['rent_amountd_per_sqr']
			res[obj_rent.id] = amounts_val
		return res
		
	def _rent_performance(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			res[obj_rent.id] = "%.2f%%" % ((obj_rent.rent_amount_base * 12) /  (obj_rent.rent_total== 0.00 and 1 or obj_rent.rent_total) * 100)
		return res
		
	def _rent_amount_years(self,cr,uid,ids,field_name,args,contexto):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			years_val = {}
			
			percentaje = obj_rent.rent_rise
			debug(percentaje)
			years_val['rent_rise_year2'] = obj_rent.rent_amount_base * (1 + float(percentaje) / 100)
			years_val['rent_rise_year3'] = years_val['rent_rise_year2']  * (1 + float(percentaje) / 100)
			
			to_exchange = {
				'obj_rent'      : obj_rent,
				'vals'          : [('rent_rise_year2d',years_val['rent_rise_year2']),
				('rent_rise_year3d',years_val['rent_rise_year3']),
				('rent_amountd_base',obj_rent.rent_amount_base),
				],
				'from_currency' : obj_rent.currency_id,
				'to_currency'   : obj_rent.eqv_currency_id,
			}
			
			exchanged = self._calculate_exchange(cr,uid,ids,to_exchange)
			years_val['rent_rise_year2d'] = exchanged['rent_rise_year2d']
			years_val['rent_rise_year3d'] = exchanged['rent_rise_year3d']
			
			#Just to avoid use a separate function
			years_val['rent_amountd_base'] = exchanged['rent_amountd_base']
			res[obj_rent.id] = years_val
		return res
		
	def inv_line_create(self, cr, uid,obj_rent,args,type='rent'):
		res_data = {}
		obj_company = obj_rent.rent_rent_client_id.company_id or False
		
		if type=='rent':
			res_data['account_id'] = obj_rent.rent_rent_account_id.id
		elif type == 'main':
			res_data['account_id'] = obj_rent.rent_rent_main_account_id.id
		if obj_company.currency_id.id != obj_rent.currency_id.id:
			new_price = res_data['price_unit'] * obj_rent.currency_id.rate
			res_data['price_unit'] = new_price

		return (0, False, {
			'name': args['desc'],
			'account_id': res_data['account_id'],
			'price_unit': args['amount'] or 0.0,
			'quantity': 1 ,
			'product_id': False,
			'uos_id': False,
			'invoice_line_tax_id': [(6, 0, [])],
			'account_analytic_id': False,
			'invoice_rent_id': args['rent_id'] or False,
		})
	
	def invoice_rent(self, cr, uid, ids, args,type='rent',current_date=date.today()):
		#Creates the invoice for every rent given as arg, the args is a list of dictionaries 
		#usually it only has one element. But it can take up 2 records to create an invoice with 2 lines
		res = {}
		journal_obj = self.pool.get('account.journal')
		il = []
		debug('GENERACION DE factura PAGO')
		debug(args)
		
		for rlist in args:
			obj_rent = self.browse(cr,uid,rlist['rent_id'])
			il.append(self.inv_line_create(cr, uid,obj_rent,rlist,type))

		obj_client = obj_rent.rent_rent_client_id
		a = obj_client.property_account_receivable.id
		journal_ids = journal_obj.search(cr, uid, [('type', '=','sale'),('company_id', '=',obj_client.company_id.id)],limit=1)

		if not journal_ids:
			raise osv.except_osv(_('Error !'),
				_('There is no purchase journal defined for this company: "%s" (id:%d)') % (o.company_id.name, o.company_id.id))
		desc = 'Factura por concepto de alquiler de  %s' % (obj_rent.rent_related_real)
		
		#Determines if today is the previous month for the invoice creation
		today = current_date
		debug(today)
		if type=='rent':
			date_due = (obj_rent.rent_invoiced_day <= obj_rent.rent_charge_day and date(today.year,today.month,1) or (today.replace(day=1) + timedelta(days=32)).replace(day=1))
			date_due = date_due.replace(day=obj_rent.rent_charge_day + obj_rent.rent_grace_period)
		elif type == 'main':
			date_due = (obj_rent.rent_main_invoiced_day <= obj_rent.rent_main_charge_day and date(today.year,today.month,1) or (today.replace(day=1) + timedelta(days=32)).replace(day=1))
			date_due = date_due.replace(day=obj_rent.rent_main_charge_day + obj_rent.rent_main_grace_period)
		
		inv = {
			'name': obj_rent.name or desc,
			'reference': obj_rent.name or desc,
			'account_id': a,
			'type': 'out_invoice',
			'partner_id': obj_client.id,
			'currency_id': obj_rent.currency_id.id,
			'address_invoice_id': obj_client.address[0].id,
			'address_contact_id': obj_client.address[0].id,
			'journal_id': len(journal_ids) and journal_ids[0] or False,
			'origin': obj_rent.name or desc,
			'invoice_line': il,
			'fiscal_position': obj_client.property_account_position.id,
			'payment_term': obj_client.property_payment_term and o.partner_id.property_payment_term.id or False,
			'company_id': obj_client.company_id.id,
			'date_invoice' : today,
			'date_due' : date_due,
		}
		inv_id = self.pool.get('account.invoice').create(cr, uid, inv, {'type':'out_invoice'})
		self.pool.get('account.invoice').button_compute(cr, uid, [inv_id], {'type':'out_invoice'}, set_total=True)
		res['invoice_id'] = inv_id
		res['rent_id'] = obj_rent.id
		res['invoice_type'] = type
		self.register_rent_invoice(cr,uid,ids,res)
		return res
	
	def first_rent(self,cr,uid,ids,type='rent',current_date=date.today()):
		#for the given list of ids it creates a list of the invoice data and later calls 
		#the invoice_rent to create every invoice
		debug('GENERACION DE PRIMER PAGO')
		res = []
		debug(ids)
		for obj_rent in ids:
			today = current_date
			charge_date = date(today.year,today.month,1)
			 
			if type == 'rent':
				init_date = parser.parse(obj_rent.rent_start_date).date()
			elif type == 'main':
				init_date = parser.parse(obj_rent.rent_main_start_date).date()
			
			init_date = init_date.replace(year=today.year)
			
			if (type == 'main' and obj_rent.rent_main_inc) or type == 'rent':
				res.append(self._invoice_data(cr,uid,ids,obj_rent,{'init_date': init_date, 'end_date' : charge_date.replace(day=calendar.mdays[charge_date.month])},type))
			self.invoice_rent(cr,uid,ids,res,type)
		return True
	
	def _invoice_main_required(self,cr,uid,ids,type='rent',current_date=date.today()):
		#determines if the ids given require a invoice for the month
		res = {}
		for obj_rent in self.browse(cr,uid,ids):
			is_required = False
			today = current_date
			if type == 'rent':
					invoice_day = (obj_rent.rent_invoiced_day <= obj_rent.rent_charge_day and obj_rent.rent_charge_day - obj_rent.rent_invoiced_day or calendar.mdays[today.month] - obj_rent.rent_invoiced_day +  obj_rent.rent_charge_day + 1)
					inv_rent_list = obj_rent.rent_invoice_ids
			elif type == 'main':
					invoice_day = (obj_rent.rent_main_invoiced_day <= obj_rent.rent_main_charge_day and obj_rent.rent_main_charge_day - obj_rent.rent_main_invoiced_day or calendar.mdays[today.month] - obj_rent.rent_main_invoiced_day + obj_rent.rent_main_charge_day + 1)
					inv_rent_list = obj_rent.rent_main_invoice_ids
			if today.day == invoice_day:
				if (type == 'main' and obj_rent.rent_main_inc) or type == 'rent':
					is_required = True
					for obj_inv_reg in inv_rent_list:						
						inv_date = parser.parse(obj_inv_reg.invoice_date).date()
						debug(today)
						debug(inv_date)
						if type == 'rent':
							start_date = parser.parse(obj_rent.rent_start_date).date()
						elif type == 'main':
							start_date = parser.parse(obj_rent.rent_main_start_date).date()
						if inv_date.month == start_date.month and inv_date.year == start_date.year and len(inv_rent_list) <= 1:
							debug("SOLO TIENE 1 FACTURA")
							is_required = True
						elif inv_date.month == today.month and inv_date.year == today.year:
							debug("Tiene TIENE mas de una FACTURA")
							is_required = False
							break
			res[obj_rent.id] = is_required
		return res
	
	def register_rent_invoice(self,cr,uid,ids,args):
		obj_rent = self.browse(cr,uid,args['rent_id'])
		obj_rent.write({'rent_invoice_ids' : [(0,0,{'invoice_id':args['invoice_id'],'invoice_rent_id':obj_rent.id,'invoice_type':args['invoice_type']})]})
		return True
	
	def rent_calc(self,cr,uid,ids,type='rent',current_date=date.today()):
		#calculates the rent considering the date of change for the anual rate.
		debug('GENERACION DE Pago Normal')
		res = {}
		for obj_rent in ids:
			res_dob_inv = []
			debug(current_date)
			today = current_date
			
			if type=='rent':
				rise_date = parser.parse(obj_rent.rent_start_date).date()
				charge_date = (obj_rent.rent_invoiced_day <= obj_rent.rent_charge_day and date(today.year,today.month,1) or (today.replace(day=1) + timedelta(days=32)).replace(day=1))
			elif type == 'main':
				rise_date = parser.parse(obj_rent.rent_main_start_date).date()
				charge_date = (obj_rent.rent_main_invoiced_day <= obj_rent.rent_main_charge_day and date(today.year,today.month,1) or (today.replace(day=1) + timedelta(days=32)).replace(day=1))
				
			rise_date = rise_date.replace(year=today.year)
			
			debug(rise_date)
			debug(charge_date)
			if rise_date.month == charge_date.month:
				res_dob_inv.append(self._invoice_data(cr,uid,ids,obj_rent,{'init_date': charge_date, 'end_date' : rise_date.replace(day=rise_date.day-1)},type))
				
				#We need to update the amount_base of the rent, so we ca
				#charge the next part with the rate included
				if type=='rent':
					self.register_historic(cr,uid,obj_rent)
				elif type=='main':
					self.register_main_historic(cr,uid,obj_rent)
				obj_rent = self.browse(cr,uid,obj_rent.id)
				res_dob_inv.append(self._invoice_data(cr,uid,ids,obj_rent,{'init_date': rise_date, 'end_date' : charge_date.replace(day=calendar.mdays[charge_date.month])},type))
			else:
				res_dob_inv.append(self._invoice_data(cr,uid,ids,obj_rent,{'init_date': charge_date, 'end_date' : charge_date.replace(day=calendar.mdays[charge_date.month])},type))
			
			debug(res_dob_inv)
			self.invoice_rent(cr,uid,ids,res_dob_inv,type,today)
		return True
	
	def _invoice_data(self,cr,uid,ids,obj_rent,date_range,type='rent'):
		#creates a dictionary with all the needed data of the rent or maintenance
		init_date = date_range['init_date']
		end_date = date_range['end_date']
		month_days = calendar.mdays[init_date.month]
		charged_days = month_days
		if (end_date.day == month_days and init_date.day != 1) or (end_date.day != month_days and init_date.day == 1):
			charged_days = (end_date.day - init_date.day) + 1
		if type == 'rent':
			amount_base = obj_rent.rent_amount_base
		elif type == 'main':
			amount_base = obj_rent.rent_main_amount_base
		
		amount =  charged_days / float(month_days) * amount_base
		desc = "Cobro de %s. Desde el %s hasta el %s" % ((type=='rent'and 'alquiler' or 'Mantenimiento'),init_date.strftime("%A %d %B %Y"),end_date.strftime("%A %d %B %Y"))
		
		res = {
			'rent_id': obj_rent.id,
			'amount' : amount,
			'date'   : end_date,
			'desc'   : desc,
		}
		return res
	def day_invoice_check(self,cr,uid):
		#MAIN CRONJOB TO BE RUNNED EVERY DAY AN CREATE INVOICES
		self.cron_rent_invoice(cr,uid,[])
		return True
	def cron_rent_invoice(self,cr,uid,ids,context):
		#gets the list of all active rents
		rent_ids = self.search(cr,uid,[('state','=','active')])
		date_list = []
		debug('CRONJOB FORCED TEST')
		#we retrieve the date of today and the last date registered at the log 
		#this allows to create the list with dates between those two
		today =date.today()
		debug(today)
		log_id = self.pool.get('rent.invoice.log').search(cr,uid,[],order='log_date desc')
		debug(log_id)
		if log_id:
			last_log = self.pool.get('rent.invoice.log').browse(cr,uid,log_id[0])
			debug(last_log.log_date)
			last_date = parser.parse(last_log.log_date).date() + timedelta(days=1)
		else:
			#if theres no record we set the today as the last_date assuming that 
			#the cronjob has never been excecuted and add it to the list
			last_date = today
		
		debug(last_date)
		while last_date <= today:
			date_list.append(last_date)
			last_date += timedelta(days=1)
		debug(date_list)
		#once we have all that dates we run the method for each one 
		#NOTE: date_list contains at least the today date
		for record_date in date_list:
			is_required = self._invoice_main_required(cr,uid,rent_ids,'rent',record_date)
			self._method_invoice_caller(cr,uid,rent_ids,is_required,'rent',record_date)
		
			#after we invocied all the rents, now we can proceed with the maintenance 
			debug("CALCULATING INVOICE FOR MAINTENANCE")
			is_required = self._invoice_main_required(cr,uid,rent_ids,'main',record_date)
			self._method_invoice_caller(cr,uid,rent_ids,is_required,'main',record_date)
		debug(date_list)
		if date_list:
			log_desc = "CronJob ran for dates between %s to %s" % (date_list[0].strftime("%A %d %B %Y"),(len(date_list) > 1 and date_list[-1] or date_list[0]).strftime("%A %d %B %Y"))
			self.pool.get('rent.invoice.log').create(cr,uid,{'log_date':today,'log_desc' : log_desc })
		return True
	
	def _method_invoice_caller (self,cr,uid,rent_ids,is_required,type='rent',current_date=date.today()):
		res_norm_inv = []
		for obj_rent in self.browse(cr,uid,rent_ids):
			if is_required[obj_rent.id]: 
				#res_norm_inv.append(obj_rent.id)
				res_norm_inv.append(obj_rent)
		self.rent_calc(cr,uid,res_norm_inv,type,current_date)
		return True
	
	def cron_rent_defaulter_interest(self,cr,uid):
		#under develop
		rent_ids = self.search(cr,uid,[('state','=','active')])
		res = []
		for obj_rent in self.browse(cr,uid,rent_ids):
			today = date.today()
			invoices_ids = self.pool.get('rent.rent.invoice').search(cr,uid,[('invoice_date','=',today.strftime('%Y-%m-%d'))])
			for obj_invoice_rent in self.pool.get('rent.invoice.rent').browse(cr,uid,invoices_ids):
				#date_due = parser.parse(obj_invoice_rent.date_due).date()
				today = date.today()
				limit_day = parser.parse(obj_invoice_rent.date_due).date().day + (obj_rent.rent_grace_period or 0)
				if  (today.day > 8 and today.day > limit_dayand) and obj_invoice_rent.residual != 0:
					res.append(obj_invoice_rent)
		return True
		
	def action_first_invoice(self,cr,uid,ids,context=None):
		#gets the list of all active rents
		rent_ids = self.search(cr,uid,[('state','=','active')])
		#is_required = self._invoice_required(cr,uid,rent_ids)
		res_first_inv = []
		res_first_main_inv = []
		debug("CAMBIO DE ESTADOSSSSSSSSSSSSSSSSSS")
		debug(rent_ids)
		for obj_rent in self.browse(cr,uid,rent_ids):
			#if is_required[obj_rent.id]: 
			has_first = self.pool.get('rent.invoice.rent').search(cr,uid,[('invoice_rent_id','=',obj_rent.id),('invoice_type','=','rent')])
			if not has_first and parser.parse(obj_rent.rent_start_date).date().month == date.today().month:
				#res_first_inv.append(obj_rent.id)
				res_first_inv.append(obj_rent)
				percentaje = obj_rent.rent_performance.split('%')[0]
				#we update the estimates list for the obj
				obj_rent.write({'rent_estimates_ids' : [(0,0,{'estimate_performance': float(percentaje),'estimate_rent_id':obj_rent.id,'estimate_date' : date.today(), 'estimate_state':'final'})]})
				
			#We check for maintenance invoice for this we need to heck if the rent hasta a maintenance record
			if obj_rent.rent_main_inc:
				has_main_first = self.pool.get('rent.invoice.rent').search(cr,uid,[('invoice_rent_id','=',obj_rent.id),('invoice_type','=','main')])
				if not has_main_first and parser.parse(obj_rent.rent_main_start_date).date().month == date.today().month:
					res_first_main_inv.append(obj_rent)
					percentaje = obj_rent.rent_main_performance.split('%')[0]
					obj_rent.write({'rent_main_estimates_ids' : [(0,0,{'estimate_performance': float(percentaje),'estimate_rent_id':obj_rent.id,'estimate_date' : date.today(), 'estimate_state':'final'})]})
		
		debug(res_first_inv)
		debug(res_first_main_inv)
		self.first_rent(cr,uid,res_first_inv)
		self.first_rent(cr,uid,res_first_main_inv,'main')
		return {}
	
	def calculate_negotiation(self,cr,uid,ids,context=None):
		res = {}
		#for obj_rent in self.browse(cr,uid,ids):
		#	current_currency = obj_rent.currency_id
		#	obj_client = obj_rent.rent_rent_client_id
		#	company_currency = (obj_client.company_id and obj_client.company_id.currency_id.id or self._get_currency(cr,uid,context))
		#	if company_currency  == current_currency.id:
		#		if current_currency.name != "USD":
		#			res['eqv_currency_id'] = pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('name','=','USD')])[0]
		#		else:
		#			res['eqv_currency_id'] = company_currency
		#	if company_currency  != current_currency.id:
		#		res['eqv_currency_id'] = company_currency
		#	
		#	obj_rent.write({'currency_id': current_currency.id, 'eqv_currency_id': res['eqv_currency_id']})
		return { 'value' : res}
	
	def _calculate_exchange(self,cr,uid,ids,args,context=None):
		val = {}
		if args:
			#we search for all the variables so we can exchange currencies
			obj_rent = args['obj_rent']
			obj_client = obj_rent.rent_rent_client_id
			orig_currency  = args['from_currency']
			dest_currency  = args['to_currency']
			#Main currency required, for now we asume its the USD
			main_currency = pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('rate','=', 1.0)])[0]
			for record in args['vals']:
				value = record[1]
				if (orig_currency.id != dest_currency.id):
					value = value / orig_currency.rate
					if dest_currency.id != main_currency:
						value = value * dest_currency.rate
				val[record[0]] = value
		return val
	def _rent_main_performance(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			total = 1
			debug(obj_rent.rent_main_total)
			res[obj_rent.id] = "%.2f%%" % ((obj_rent.rent_main_amount_base * 12) /  (obj_rent.rent_main_total== 0.00 and 1 or obj_rent.rent_main_total) * 100) 
			debug(res)
		return res
		
	def _rent_main_amount_years(self,cr,uid,ids,field_name,args,contexto):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			years_val = {}

			percentaje = obj_rent.rent_main_rise
			years_val['rent_main_rise_year2'] = obj_rent.rent_main_amount_base * (1 + float(percentaje) / 100)
			years_val['rent_main_rise_year3'] = years_val['rent_main_rise_year2']  * (1 + float(percentaje) / 100)
			
			to_exchange = {
				'obj_rent'      : obj_rent,
				'vals'          : [('rent_main_rise_year2d',years_val['rent_main_rise_year2']),
				('rent_main_rise_year3d',years_val['rent_main_rise_year3']),
				('rent_main_amountd_base',obj_rent.rent_main_amount_base),
				],
				'from_currency' : obj_rent.currency_id,
				'to_currency'   : obj_rent.eqv_currency_id,
			}
			
			exchanged = self._calculate_exchange(cr,uid,ids,to_exchange)
			years_val['rent_main_rise_year2d'] = exchanged['rent_main_rise_year2d']
			years_val['rent_main_rise_year3d'] = exchanged['rent_main_rise_year3d']
			
			#Just to avoid use a separate function
			years_val['rent_main_amountd_base'] = exchanged['rent_main_amountd_base']
			
			res[obj_rent.id] = years_val
		return res
	
	_columns = {
		'name'                  : fields.char('Name',size=64),
		'rent_rent_client_id'   : fields.many2one('res.partner','Client', required=True, states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_end_date'         : fields.date('Ending Date', required=True, states={'active':[('readonly',False)], 'finished':[('readonly',True)]}),
		'rent_ending_motif'     : fields.selection([('early','Early Return'),('expiration','Contract Expiration'),('eviction','No payment eviction'), ('others','Various problems with tenant')],'Ending Motif'),
		'rent_ending_motif_desc': fields.text('Ending Motif Description'),
		
		'rent_rise'             : fields.float('Anual Rise', required=True, states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		#'rent_rise'             : fields.char('Anual Rise',size=64, required=True, states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_amount_base'      : fields.float('Final Price $', required=True, states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_performance'      : fields.function(_rent_performance, type='char',method = True,string='Performance'),
		'rent_rise_year2'       : fields.function(_rent_amount_years, type='float',method = True,string='Year 2 $', multi='Years'),
		'rent_rise_year3'       : fields.function(_rent_amount_years, type='float',method = True,string='Year 3 $', multi='Years'),
		'rent_amount_per_sqr'   : fields.function(_performance_per_sqr, type='float',method = True,string='Amount per Sqr', multi='negot'),
		
		'rent_amountd_per_sqr'  : fields.function(_performance_per_sqr, type='float',method = True,string='Amount m2 $', multi='negot'),
		'rent_amountd_base'     : fields.function(_rent_amount_years, type='float',method = True,string='Final Price $', multi='Years'),
		'rent_rise_year2d'      : fields.function(_rent_amount_years, type='float',method = True,string='Year 2  $', multi='Years'),
		'rent_rise_year3d'      : fields.function(_rent_amount_years, type='float',method = True,string='Year 3  $', multi='Years'),
		'rent_show_us_eq'       : fields.boolean('Check USD Currency Equivalent',store=False),
		'rent_total_us'         : fields.function(_get_total_rent,type='float',method=True,string='Total Paid',multi='total'),
		
		'rent_type'             : fields.selection([('Contract','Contract'),('Adendum','Adendum'),('Renovation','Renovation')],'Type', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'state'                 : fields.selection([('active','Active'),('finished','Inactive'),('draft','Draft')],'Status', readonly=True),
		'rent_start_date'       : fields.date('Starting Date', required=True, states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_total'            : fields.function(_get_total_rent,type='float',method=True,string='Total Paid',multi='total'),
		'rent_rent_local_id'    : fields.many2one('rent.floor.local','Local', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_rent_parking_id'  : fields.many2one('rent.floor.parking','Parking', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_rent_estate_id'   : fields.many2one('rent.estate','Estate', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_related_real'     : fields.selection([('local','Locals'),('parking','Parking'),('estate','Estates')],'Type of Real Estate', required=True,states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_years'            : fields.function(_calculate_years,type='integer',method=True,string = 'Years' ,help='Check if you want to calculate a rent for locals'),
		'rent_modif'            : fields.one2many('rent.rent', 'rent_modif_ref','Contract reference', states={'draft':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_modif_ref'        : fields.many2one('rent.rent', 'Modifications',ondelete='cascade'),
		'currency_id'           : fields.many2one('res.currency', 'Currency', required=True),
		'eqv_currency_id'       : fields.many2one('res.currency', 'Currency Equivalence', required=True),
		'rent_estimates_ids'    : fields.one2many('rent.rent.estimate', 'estimate_rent_id','Estimates',states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),         
		'rent_historic_ids'     : fields.one2many('rent.rent.anual.value', 'anual_value_rent_id','Historic',readonly=True, domain=[('anual_value_type', '=', 'rent')]),
		'rent_charge_day'       : fields.integer('Charge Day', required=True,help='Indica el dia del mes para realizar los cobros del alquiler.'),
		'rent_invoice_ids'      : fields.one2many('rent.invoice.rent','invoice_rent_id','Rent Invoices', domain=[('invoice_type', '=', 'rent')],readonly=True),
		'rent_invoiced_day'     : fields.integer('Invoiced Day', required=True,help='Indicates de how many days before of the charge day will create the invoice'),
		'rent_grace_period'     : fields.integer('Grace Period', required=True,help='Indicates de how many days after the charge day will allow to paid an invoice without Interest for delay'),
		
		'rent_rent_account_id'  : fields.property(
			'account.account',
			type='many2one',
			relation='account.account',
			string="Income Account",
			method=True,
			view_load=True,
			help="This account will be used for invoices instead of the default one to value sales for the current rent",required=True),
		'rent_rent_acc_int_id'  : fields.property(
			'account.account',
			type='many2one',
			relation='account.account',
			string="Interest Account",
			method=True,
			view_load=True,
			help="This account will be used for invoices instead of the default one to value expenses for the current rent",required=True),
		'rent_rent_real_area'   : fields.function(_get_total_area,type='float',method=True,string='Area'),
		
		'rent_main_inc'              : fields.boolean('Include Maintenance Rent'),
		
		#'rent_main_rise'             : fields.char('Anual Rise',size=64, states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_main_rise'             : fields.float('Anual Rise', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_main_amount_base'      : fields.float('Final Price $', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_main_performance'      : fields.function(_rent_main_performance, type='char',method = True,string='Performance'),
		'rent_main_amountd_base'     : fields.function(_rent_main_amount_years, type='float',method = True,string='Final Price $', multi='Years_main'),
		'rent_main_rise_year2'       : fields.function(_rent_main_amount_years, type='float',method = True,string='Year 2  $', multi='Years_main'),
		'rent_main_rise_year3'       : fields.function(_rent_main_amount_years, type='float',method = True,string='Year 3  $', multi='Years_main'),
		'rent_main_rise_year2d'      : fields.function(_rent_main_amount_years, type='float',method = True,string='Year 2  $', multi='Years_main'),
		'rent_main_rise_year3d'      : fields.function(_rent_main_amount_years, type='float',method = True,string='Year 3  $', multi='Years_main'),
		'rent_main_show_us_eq'       : fields.boolean('Check USD Currency Equivalent',store=False),
		'rent_main_estimates_ids'    : fields.one2many('rent.rent.main.estimate', 'estimate_maintenance_id','Estimates',states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_main_invoice_ids'      : fields.one2many('rent.invoice.rent','invoice_rent_id','Rent Invoices', domain=[('invoice_type', '=', 'main')],readonly=True),
		'rent_main_total'            : fields.float('Total Paid'),
		#'rent_main_total_us'         : fields.float('Total Paid $'),
		'rent_main_historic_ids'     : fields.one2many('rent.rent.anual.value', 'anual_value_rent_id','Historic',readonly=True, domain=[('anual_value_type', '=', 'main')]),      
		'rent_main_company_id'       : fields.many2one('res.company', 'Supplier Company'),      
		
		'rent_main_charge_day'       : fields.integer('Charge Day',help='Indica el dia del mes para realizar los cobros del alquiler.'),
		'rent_main_invoiced_day'     : fields.integer('Invoiced Day',help='Indicates de how many days before of the charge day will create the invoice'),
		'rent_main_grace_period'     : fields.integer('Grace Period',help='Indicates de how many days after the charge day will allow to paid an invoice without Interest for delay'),   
		
		'rent_rent_main_account_id'  : fields.property(
			'account.account',
			type='many2one',
			relation='account.account',
			string="Income Account",
			method=True,
			view_load=True,
			help="This account will be used for invoices instead of the default one to value sales for the current rent"),
		'rent_rent_main_acc_int_id'  : fields.property(
			'account.account',
			type='many2one',
			relation='account.account',
			string="Interest Account",
			method=True,
			view_load=True,
			help="This account will be used for invoices instead of the default one to value expenses for the current rent"),
			
		'rent_main_end_date'         : fields.date('Ending Date', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_main_start_date'       : fields.date('Starting Date', states={'active':[('readonly',True)], 'finished':[('readonly',True)]}),
	}
	
	_defaults = {
		'state'        : 'draft',
		'rent_type'    : 'Contract',
		'currency_id': _get_currency,
		'eqv_currency_id': _get_currency_eqv,
		'rent_amount_base' : 0.00,
		'rent_main_amount_base' : 0.00,
		#'rent_rise'     : "%.2f%%" % (0.),
		#'rent_main_rise': "%.2f%%" % (0.),
		'rent_charge_day' : 01,
		'rent_main_charge_day' : 01,
		'rent_main_performance' : "%.2f%%" % (0.),
	}
rent_rent()

class rent_rent_estimate(osv.osv):
	_name = 'rent.rent.estimate'
		
	def _performance_years(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_estimate in self.pool.get('rent.rent.estimate').browse(cr,uid,ids):
			if obj_estimate.estimate_performance:
				res[obj_estimate.id] = 1 / (obj_estimate.estimate_performance / 100.00)
		return res
	def _performance_amount(self,cr,uid,ids,field_name,args,context):
		res = {}
		amount = 0
		for obj_estimate in self.pool.get('rent.rent.estimate').browse(cr,uid,ids):
			obj_rent = obj_estimate.estimate_rent_id
			amounts_val = {}
			
			currency_id = obj_rent.currency_id
			debug(currency_id)
			rate_cr = currency_id.rate
			rate_us = 1
			amounts_val['estimate_amountc'] = (obj_estimate.estimate_rent_id.rent_total * (obj_estimate.estimate_performance/100.00)  / 12) / rate_us
			amounts_val['estimate_amountd'] = (obj_estimate.estimate_rent_id.rent_total * (obj_estimate.estimate_performance/100.00)  / 12) / rate_cr
			res[obj_estimate.id] = amounts_val
		return res
	def _performance_currency(self,cr,uid,ids,field_name,args,contexto):
		res = {}
		for obj_estimate in self.pool.get('rent.rent.estimate').browse(cr,uid,ids):
			obj_rent = obj_estimate.estimate_rent_id
			
			currencies_val = {}
			valor = obj_rent._get_total_area(obj_rent.id,None,None)[obj_rent.id]
			debug(valor)
			currencies_val['estimate_colones'] = obj_estimate.estimate_amountc / valor
			currencies_val['estimate_dollars'] = obj_estimate.estimate_amountd / valor
			res[obj_estimate.id] = currencies_val
		return res
	_columns = {
		'estimate_performance'       : fields.float('Performance(%)',digits=(12,2), help='This a percentaje number'),
		'estimate_years'             : fields.function(_performance_years, type='float',method = True,string='Years for reinv.'),
		'estimate_amountc'           : fields.function(_performance_amount, type='float',method = True,string='Amount', multi=True),
		'estimate_colones'           : fields.function(_performance_currency, type='float',method = True,string='c / m2',multi='Currency'),
		'estimate_amountd'           : fields.function(_performance_amount, type='float',method = True,string='Amount $', multi=True),
		'estimate_dollars'           : fields.function(_performance_currency, type='float',method = True,string='s / m2',multi='Currency'),
		'estimate_rent_id'            : fields.many2one('rent.rent','Rent'),
		'estimate_date'              : fields.date('Fecha'),
		'estimate_state'             : fields.selection([('final','Used'),('recommend','Recommend'),('min','Min'),('norec','Not Recomended')],'Status',readonly=False),
	}
	_order = "estimate_date desc"
	_defaults = {
		'estimate_date'  : date.today().strftime('%d/%m/%Y'),
	}
rent_rent_estimate()

class rent_rent_main_estimate(osv.osv):
	_name = 'rent.rent.main.estimate'
		
	def _performance_years(self,cr,uid,ids,field_name,args,context):
		res = {}
		for obj_estimate in self.pool.get('rent.rent.main.estimate').browse(cr,uid,ids):
			if obj_estimate.estimate_performance:
				res[obj_estimate.id] = 1 / (obj_estimate.estimate_performance / 100.00)
		return res
	def _performance_amount(self,cr,uid,ids,field_name,args,context):
		res = {}
		amount = 0
		for obj_estimate in self.pool.get('rent.rent.main.estimate').browse(cr,uid,ids):
			obj_rent = obj_estimate.estimate_maintenance_id
			amounts_val = {}
			
			currency_id = obj_rent.currency_id
			debug(currency_id)
			rate_cr = currency_id.rate
			rate_us = 1
			total = obj_estimate.estimate_maintenance_id.rent_main_total
			amounts_val['estimate_amountc'] = (total * (obj_estimate.estimate_performance/100.00)  / 12) / rate_us
			amounts_val['estimate_amountd'] = (total * (obj_estimate.estimate_performance/100.00)  / 12) / rate_cr
			res[obj_estimate.id] = amounts_val
		return res
	def _performance_currency(self,cr,uid,ids,field_name,args,contexto):
		res = {}
		for obj_estimate in self.pool.get('rent.rent.main.estimate').browse(cr,uid,ids):
			obj_rent = obj_estimate.estimate_maintenance_id
			
			currencies_val = {}
			valor = obj_rent._get_total_area(obj_rent.id,None,None)[obj_rent.id]
			debug(valor)
			currencies_val['estimate_colones'] = obj_estimate.estimate_amountc / valor
			currencies_val['estimate_dollars'] = obj_estimate.estimate_amountd / valor
			res[obj_estimate.id] = currencies_val
		return res
	_columns = {
		'estimate_performance'       : fields.float('Performance(%)',digits=(12,2), help='This a percentaje number'),
		'estimate_years'             : fields.function(_performance_years, type='float',method = True,string='Years for reinv.'),
		'estimate_amountc'           : fields.function(_performance_amount, type='float',method = True,string='Amount', multi=True),
		'estimate_colones'           : fields.function(_performance_currency, type='float',method = True,string='c / m2',multi='Currency'),
		
		'estimate_amountd'           : fields.function(_performance_amount, type='float',method = True,string='Amount $', multi=True),
		'estimate_dollars'           : fields.function(_performance_currency, type='float',method = True,string='s / m2',multi='Currency'),
		
		'estimate_maintenance_id'    : fields.many2one('rent.rent','Rent'),
		'estimate_date'              : fields.date('Fecha'),
		'estimate_state'             : fields.selection([('final','Used'),('recommend','Recommend'),('min','Min'),('norec','Not Recomended')],'Status',readonly=False),
	}
	_order = "estimate_date desc"
	_defaults = {
		'estimate_date'  : date.today().strftime('%d/%m/%Y'),
	}
rent_rent_main_estimate()

class rent_rent_anual_value(osv.osv):
	_name = 'rent.rent.anual.value'
	_columns = {
		'anual_value_rent_id'    : fields.many2one('rent.rent','Rent reference'),
		'anual_value_prev_value' : fields.float('Prev. Value',help='This value was taken from the record of rent at the indicated date'),
		'anual_value_value'      : fields.float('Value',help='This value was taken from the record of rent at the indicated date'),
		'anual_value_date'       : fields.date('Period'),
		'anual_value_rate'       : fields.char('Anual Rise',size=64),
		'anual_value_local_ids'      : fields.many2one('rent.floor.local','Local reference'),
		'anual_value_type'       : fields.selection([('main','Maintenance'),('rent','Rent')],'Type'),
	}
	
rent_rent_anual_value()


#This class changes the references of the invoice
#to enable it add a refeerence to the rent
class rent_invoice_line(osv.osv):
	_name = 'account.invoice.line'
	_inherit = 'account.invoice.line'
	
	def rent_id_change(self, cr, uid, ids, rent, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None):
		res = {}
		company_id = context.get('company_id',False)
		obj_rent = self.pool.get('rent.rent').browse(cr, uid, rent, context=context)		
		debug(obj_rent)		
		res['name'] = obj_rent.name
		res['price_unit'] = obj_rent.rent_amount_base
		
		if obj_rent.rent_related_real == 'estate':
			res['account_id'] = obj_rent.rent_rent_estate_id.estate_account_id
		else:
			res['account_id'] = obj_rent.rent_rent_local_id.local_building.building_estate_id.estate_account_id
			
		obj_company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
		if obj_company.currency_id.id != obj_rent.currency_id.id:
			new_price = res['price_unit'] * obj_rent.currency_id.rate
			res['price_unit'] = new_price
		debug(res)
		return {'value' : res}
	
	def onchange_type(self,cr,uid,ids,field):
		res = {}
		res['product_id'] = False
		res['invoice_rent_id'] = False
		debug(res)
		return {'value' : res}
	
	_columns = {
		'invoice_type'    : fields.selection([('rent','Rent'),('product','Product')],'Type',help = 'Select one of this to determine the type of invoice to create'),
		'invoice_rent_id'    : fields.many2one('rent.rent','Rent id'),
	}
	_defaults = {
		'invoice_type'  : 'rent',
	}
rent_invoice_line()

#This class is used to keep reference of all the invoices
#that have been register to the rent
class rent_rent_invoice(osv.osv):
	_name = 'rent.invoice.rent'
	_columns = {
		'invoice_id'       : fields.many2one('account.invoice','Invoice', ondelete='cascade'),
		'invoice_rent_id'  : fields.many2one('rent.rent', 'Rent',ondelete='cascade'),
		'invoice_date'     : fields.related('invoice_id','date_invoice', type='date',relation='account.invoice',string='Date',readonly=True,store=False),
		'invoice_amount'   : fields.related('invoice_id','amount_total', type='float',relation='account.invoice',string='Amount Total',readonly=True,store=False),
		'invoice_state'    : fields.related('invoice_id','state', type='char',relation='account.invoice',string='State',readonly=True,store=False),
		'invoice_number'   : fields.related('invoice_id','number', type='char',size=64,relation='account.invoice',string='Invoice Number',readonly=True,store=False),
		'invouce_residual' : fields.related('invoice_id','residual', type='float',relation='account.invoice',string='Residual',readonly=True,store=False),
		'invoice_type'     : fields.selection([('main','Maintenance'),('rent','Rent')],'Type'),
		
	}

rent_rent_invoice()

class rent_invoice_log(osv.osv):
	_name = 'rent.invoice.log'
	_order = 'log_date'
	_columns = {
		'log_date' : fields.date('Date'),
		'log_desc' : fields.char('Description',size=200),
		#'log_rent' : fields.many2one('rent.rent','Rent Ref'),
	}
rent_invoice_log()
#
#
class rent_contract(osv.osv):
	_name = 'rent.contract'
	
	def create(self,cr,uid, vals,context=None):
		debug("============================CREANDO EL NUEVO CONTRATO")
		contract_id = super(rent_contract,self).create(cr,uid,vals,context)
		debug(contract_id)
		obj_contract = self.pool.get('rent.contract').browse(cr,uid,contract_id)
		debug(obj_contract)
		i = 0
		for clause_perm in self.pool.get('rent.contract.clause').search(cr,uid,[('clause_is_basic','=','True')]):
		#for obj_clause_perm in self.pool.get('rent.contract.clause').browse(cr,uid,clause_perm):
			#clause_rel_id = self.pool.get('rent.contract.clause.rel').create(cr,uid,{'sequence':i,'rent_contract_id':obj_contract.id,'rent_contract_clause_id' : clause_perm},context)
			#obj_clause_perm = self.pool.get('rent.contract.clause.rel').browse(cr,uid,clause_rel_id)
			#if obj_clause_perm:
			obj_contract.write({'contract_clauses_ids' : [(0,0,{'sequence':i,'rent_contract_id':obj_contract.id,'rent_contract_clause_id' : clause_perm})]})
			i+=1
		return obj_contract.id
				
	_columns = {
		'name'             : fields.char('Reference', size=64),
		'contract_rent_id'    : fields.many2one('rent.rent','Rent Reference'),
		'contract_clauses_ids' : fields.one2many('rent.contract.clause.rel','rent_contract_id','Clausulas'),
		#'contract_clauses' : fields.many2many('rent.contract.clause','rent_contract_clause_rel','name','clause_code','Clausulas'),
		#'contract_design'  : fields.char('Design',size=64),
	}
	
rent_contract()

#
#
#
class rent_contract_template(osv.osv):
	_name = 'rent.contract.template'
rent_contract_template()

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
		'clause_is_basic' : fields.boolean('Priority', help = 'Check if the clause should allways appear on every contract you create'),
		#'clause_contract' : fields.many2many('rent.contract','rent_contract_clause','id','id','Contracts'),
	}
rent_contract_clause()


class rent_contract_clause_rel(osv.osv):
	_name = 'rent.contract.clause.rel'
	_rec_name = 'rent_contract_id'
	_columns = {
		'rent_contract_id'        : fields.many2one('rent.contract','Contract Reference'),
		'rent_contract_clause_id' : fields.many2one('rent.contract.clause','Contract Reference'),
		'sequence'                : fields.integer('Sequence'),
	}
rent_contract_clause_rel()
