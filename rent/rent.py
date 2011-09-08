from osv import osv, fields
from tools import debug
import time
import pooler
from dateutil import parser
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
		#'province_id '   : fields.selection(_get_province,'Province',size=16),
		#'canton_id'   : fields.selection(_get_canton, 'Canton'),
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
	def _determine_rented(self,cr,uid,ids,field_name,args,context):
		res = {}
		debug('Renta+==================================')
		for estate_id in ids:
			res[estate_id] =  False
			debug(ids)
			rent_ids = self.pool.get('rent.rent').search(cr,uid,[('state','=','valid'),('rent_related_real','=','estate'),('rent_rent_local','=',estate_id)])
			if rent_ids:
				res[estate_id] =  True
		debug(res)
		return res
	_columns = {
		'estate_owner'    : fields.many2one('res.company','Owner',required=True),
		'estate_number'   : fields.char('# estate', size=10,required=True),
		'estate_value'    : fields.float('VRN Dynamic',required=True),
		'estate_area'     : fields.float('Area', required=True),
		'estate_vrn_per_sqr' : fields.function(_get_estate_vrm,type='float',method=True,string='VRN Din/M2'),#fields.float('VRN Din/M2',store=False, readonly=True),
		'estate_buildings': fields.one2many('rent.building','building_estate','Buildings'),
		'estate_location' : fields.many2one('res.partner.address','Location'),
		'estate_account'  : fields.many2one('account.account', 'Cuenta'),
		'estate_rented'    : fields.function(_determine_rented,type='boolean',method=True,string='Rented',help='Checked if the local is rented'),
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
		'building_gallery_photo'     : fields.char('Gallery of Photos', size=64),
		'building_floors'            : fields.one2many('rent.floor','floor_building','Floors'),
		'building_vrn_per_sqr'       : fields.function(_get_building_vrm,type='float',method=True,string='VRN Din/M2'),
		'building_code'              : fields.char('Code', size=4, required=True),
		'building_asset'             : fields.many2one('account.asset.asset','Asset'),
	}
rent_building()

#Class that represents every single floor contained on the building, defined above
#All floors are differenced by the number starting from 0 (basement), then higher 
#the numbre then near to the top of the building is the floor.
class rent_floor(osv.osv):
	_name = 'rent.floor'
	_rec_name = 'floor_number'
	
	def _calculate_floor_value(self,cr,uid,ids,field_name,args,context):
		#This method takes al the valid rents for the floor and calculates the value according to 
		#the value of the locals,parking, building and estate related to it
		res = {}
		valores = {}
		total = 0
	#	debug("CALCULO====================")
	#	debug(ids)
		for floor_id in ids:
	#		debug(floor_id)
			actual_rent = self.pool.get('rent.rent').search(cr,uid,['|',('state','=','valid'),('state','=','draft'),('rent_related_real','=','local')])
	#		debug(actual_rent)
			for obj_rent in self.pool.get('rent.rent').browse(cr,uid,actual_rent):
				obj_local = obj_rent.rent_rent_local
				local_floor_ids = self.pool.get('rent.local.floor').search(cr,uid,[('local_local_floor','=',obj_local.id),('local_floor_floor','=',floor_id)])
				for local in self.pool.get('rent.local.floor').browse(cr,uid,local_floor_ids):
					valores = local._local_value(local.id,None,None)
	#				debug(valores)
					total += valores[local.id]
	#		debug(total)
			
			#This part look for the parking on rents associated to the floor
			rent_ids = self.pool.get('rent.rent').search(cr,uid,['|',('state','=','valid'),('state','=','draft'),('rent_related_real','=','parking')])
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_ids)
			for rent in obj_rent:
				obj_parking = rent.rent_rent_parking
				if (obj_parking.parking_floor.id == floor_id):
					total += obj_parking._parking_value(obj_parking.id,None,None)[obj_parking.id]
			res[floor_id] = total
			total = 0
		return res
	
	def _get_fullname(self,cr,uid,ids,field_name,args,context):
		debug("FULLNAME====================")
		res = {}
		for obj_floor in self.pool.get('rent.floor').browse(cr,uid,ids):
			building_code = obj_floor.floor_building.building_code
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
		#'floor_local'      : fields.one2many('rent.floor.local','local_floor','Local'),
		'floor_parking'    : fields.one2many('rent.floor.parking','parking_floor','Parking'),
		'floor_building'   : fields.many2one('rent.building','Building'),
		'complete_name'    : fields.function(_get_fullname,type='char',method=True,string='Name',help='This name uses the code of the building and the floor name'),
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
	#	debug('EDIFICIO+==================================')
	#	debug(ids)
		for local_id in ids:
			local = self.pool.get('rent.local.floor').search(cr,uid,[('local_local_floor','=',local_id)])
	#		debug(local)
			res[local_id] = False
			for lids in local:
				obj_local = self.pool.get('rent.local.floor').browse(cr,uid,lids)
	#			debug(obj_local)
				res[local_id] = obj_local.local_floor_floor.floor_building.id
	#		debug(res)
		return res
	
	def _determine_rented(self,cr,uid,ids,field_name,args,context):
		res = {}
	#	debug('Renta+==================================')
		for local_id in ids:
			res[local_id] =  False
	#		debug(ids)
			rent_ids = self.pool.get('rent.rent').search(cr,uid,[('state','=','valid'),('rent_related_real','=','local'),('rent_rent_local','=',local_id)])
			if rent_ids:
				res[local_id] =  True
	#	debug(res)
		return res
	def _local_value(self,cr,uid,ids,field_name,args,context):
		res = {}
	#	debug(ids)
		total = 0
		for local in self.pool.get('rent.floor.local').browse(cr,uid,ids):
			for obj_local_floor in local.local_local_by_floor:
				total += obj_local_floor._local_value(obj_local_floor.id,None,None)[obj_local_floor.id]
			res[local.id] = total
			total = 0
	#	debug(total)
	#	debug(res)
		return res

	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['local_number','local_building'], context=context)
		res = []
	#	debug('NOMBREPISOS+==================================')
		for record in reads:
	#		debug(record)
	#		debug(record['local_building'][1])
			name = 'Local #' + str(record['local_number']) + ' , ' +  record['local_building'][1]
		#	for subrecord in subreads 
		#		name += ', ' + subrecord['local_floor_building']
			res.append((record['id'], name))
		return res
	
	#This method takes the area of every record of local_by_floor and calculates the total area
	def _local_area(self,cr,uid,ids,field_name,args,context):
		res = {}
	#	debug ("AREA TOTAL")
		for obj_local in self.pool.get('rent.floor.local').browse(cr,uid,ids):
	#		debug(obj_local.local_local_by_floor)
			total = 0
			for obj_local_floor in obj_local.local_local_by_floor:
				total += obj_local_floor.local_floor_area
	#		debug(total)
			res[obj_local.id] = total
		return res
	_columns = {
		'local_area'               : fields.function(_local_area,type='float',method=True,string='VRN Dynamic'),
		#'local_area'               : fields.float('Area',required=True),
		#'local_value'              : fields.float('Value',required=True),
		'local_number'             : fields.integer('# Local',required=True),
		'local_huella'             : fields.float('Huella',required=True),
		'local_water_meter_number' : fields.char('Water Meter',size=64), 
		'local_light_meter_number' : fields.char('Electric Meter', size=64),
		#'local_sqrmeter_price'     : fields.function(_local_sqr_price,type='float',method=True,string='Sqr Meter Price'),
		#'local_sqrmeter_price'     :  fields.float('Sqr Meter Price',required=True),
		'local_rented'             : fields.function(_determine_rented,type='boolean',method=True,string='Rented',help='Check if the local is rented'),
		#'local_floor'              : fields.many2one('rent.floor','# Floor'),
		'local_local_by_floor'     : fields.one2many('rent.local.floor','local_local_floor','Local floors'),
		#'local_floor'              : fields.related('rent.local.floor','# Floor'),
		'local_building'           : fields.function(_get_building_local,type='many2one',obj='rent.building',method=True,string='Building'),
		'local_gallery_photo'      : fields.char('Photo Gallery', size=64),
		'local_photo'              : fields.binary('Main photo'),
		#'local_rent'               : fields.many2one('rent.rent','Alquiler'),
	}
rent_floor_local()

class rent_local_floor(osv.osv):
	_name = 'rent.local.floor'
	
	def _local_sqr_price(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_id)
			obj_build = obj.local_floor_floor.floor_building
			res[local_id] = obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
	
	def _local_value(self,cr,uid,ids,field_name,args,context):
		res = {}
		for local_id in ids:
			obj = self.pool.get('rent.local.floor').browse(cr,uid,local_id)
			obj_build = obj.local_floor_floor.floor_building
			res[local_id] = obj.local_floor_area * obj_build._get_building_vrm(obj_build.id,None,None)[obj_build.id]
		return res
		
	#def _local_floor_area(self,cr,uid,ids,field_name,args,context):
	#	res = {}
	#	for local_floor_id in ids:
	#		obj = self.pool.get('rent.local.floor').browse(cr,uid,local_floor_id)
	#		res[local_floor_id] = obj.local_floor_width * obj.local_floor_large
	#	return res
	
	def onchange_floor(self,cr,uid,ids,floor_id):
		res = {}
		debug("+============================")
		obj_floor = self.pool.get('rent.floor').browse(cr,uid,floor_id)
		debug(obj_floor)
		res['local_floor_building'] = obj_floor.floor_building.id
		debug(res)
		return {'value' : res}
	_columns = {
		#'name'                 : fields.char('Reference',size=64,help='Indicate a representative reference for the asociation'),
		'local_floor_front'    : fields.float('Front', required=True),
		'local_floor_side'    : fields.float('Side', required=True),
		'local_floor_floor'    : fields.many2one('rent.floor','Level',help='Represents the floor on witch its located the local'),
		'local_local_floor'    : fields.many2one('rent.floor.local','Local#',help='Represents the floor on witch its located the local'),
		#'local_rent'           : fields.many2one('rent.rent','Alquiler',ondelete='cascade'),
		'local_floor_area'     : fields.float('Area M2',required=True),
		#'local_floor_area'     : fields.function(_local_floor_area,type='float',method=True,string='Area M2'),
		'local_sqrmeter_price' : fields.function(_local_sqr_price,type='float',method=True,string='Sqr Meter Price'),
		'local_floor_value'    : fields.function(_local_value,type='float',method=True,string='Total Value'),
		'local_floor_building' : fields.related('local_floor_floor','floor_building',type='many2one',relation='rent.building',string='Building', readonly=True, store=False),
	} 
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
	
	def name_get(self, cr, uid, ids, context=None):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['parking_number','parking_floor'], context=context)
		res = []
		debug('NOMBREPARKEO+==================================')
		for record in reads:
			debug(record)
			debug(record['parking_floor'][1])
			name = 'Parking #' + str(record['parking_number']) + ' , ' +  record['parking_floor'][1]
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
			rent_ids = self.pool.get('rent.rent').search(cr,uid,[('state','=','valid'),('rent_related_real','=','parking'),('rent_rent_parking','=',parking_id)])
			if rent_ids:
				res[parking_id] =  True
		debug(res)
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
		'parking_rented'          : fields.function(_determine_rented,type='boolean',method=True,string='Rented',help='Checked if the parking is rented'),
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
	
	def onchange_estimations(self,cr,uid,ids,field):
		res = {}
		debug("==========ESTIMACIONES====")
		debug(field)
		obj_sorted = sorted(field,key=lambda estimate: estimate.estimate_performance,reverse=True)
		vals = {}
		priority = 1
		for obj_record in obj_sorted:
			if priority == 1:
				vals['estimate_state'] = 'recommend'
			elif priority == 2:
				vals['estimate_state'] = 'min'
			else:
				vals['estimate_state'] = 'norec'
			debug(vals)
			obj_record.write(vals)
			priority += 1
		return True
		
	def _get_total_area(self,cr,uid,ids,fields_name,args,context):
		res = {}
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			if obj_rent.rent_related_real == 'local':
				total = obj_rent.rent_rent_local.local_area
			elif obj_rent.rent_related_real == 'parking':
				#debug("PARQUEO")
				total = obj_rent.rent_rent_parking.parking_area
			else:
				#debug("LOTES")
				total = obj_rent.rent_rent_estate.estate_area
			res[obj_rent.id] = total
		return res
		
	def _get_currency(self, cr, uid, context=None):
		user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, [uid], context=context)[0]
		if user.company_id:
			return user.company_id.currency_id.id
		return pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('rate','=', 1.0)])[0]
		
	def _get_total_rent(self,cr,uid,ids,field_name,args,context):
		res = {}
		total = 0
		#debug('+==================================')
		for rent_id in ids:
			#debug(rent_id)
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_id)
			debug(obj_rent)
			if obj_rent.rent_related_real == 'local':
			#	debug("LOCALES")
			#	debug(obj_rent.rent_rent_local)
				obj_local = obj_rent.rent_rent_local
				total = obj_local._local_value(obj_local.id,None,None)[obj_local.id]
			#	debug(total)
			elif obj_rent.rent_related_real == 'parking':
			#	debug("PARQUEO")
				obj_parking = obj_rent.rent_rent_parking
			#	debug(obj_parking)
				total = obj_parking._parking_value(obj_parking.id,None,None)[obj_parking.id]
			else:
			#	debug("LOTES")
			#	debug(obj_rent.rent_rent_estate)
				obj_estado = obj_rent.rent_rent_estate
				total = obj_estado._get_estate_vrm(obj_estado.id,None,None)[obj_estado.id]
			#	debug(total)
			res[rent_id] = total
		return res
		
	def _calculate_years(self,cr,uid,ids,field_name,args,context):
		#debug('+==================================')
		res = {}
		for rent_id in ids:
			obj_rent = self.pool.get('rent.rent').browse(cr,uid,rent_id)
			if (obj_rent.rent_end_date and  obj_rent.rent_start_date):
				fin = parser.parse(obj_rent.rent_end_date)
				inicio = parser.parse(obj_rent.rent_start_date)
			#	debug(inicio)
			#	debug(fin)
				res[rent_id] = (fin.year - inicio.year)
			#debug(res)
		return res
	
	def write(self, cr, uid, ids, vals, context=None):
		obj_rent = self.pool.get('rent.rent').browse(cr,uid,ids)[0]
		if 'rent_related_real' in vals:			
			#debug('_---------------------------------------------------ACT')
			
			#debug(obj_rent)
			#debug(obj_rent.rent_rent_local)
			if (obj_rent.rent_related_real != vals['rent_related_real']):
			#	debug(vals)
				real_type = vals['rent_related_real'] 
				if real_type == 'local' or real_type == 'parking':
					vals['rent_rent_estate'] = False
				if real_type == 'local' or real_type == 'estate':
					vals['rent_rent_parking'] = False
				if real_type == 'parking' or real_type == 'estate':
					vals['rent_rent_local'] = False
		#debug(vals)
		super(rent_rent, self).write(cr, uid, ids, vals, context=context)
		if 'rent_estimates' in vals:
			obj_rent.onchange_estimations(obj_rent.rent_estimates)
		return True
		
	def _performance_per_sqr(self,cr,uid,ids,field_name,args,context):
		res = {}
		debug("=============================_performance_per_sqr")
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			debug(obj_rent)
			valor = obj_rent._get_total_area(obj_rent.id,None,None)[obj_rent.id]
			debug(valor)
			res['rent_amount_per_sqr'] = 1# obj_rent.rent_amount_base / valor
		debug(res)
		return res
		
	def _rent_performance(self,cr,uid,ids,field_name,args,context):
		res = {}
		debug("=============================RENT PERFORMANCE")
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			debug(obj_rent)
			res['rent_performance'] = 1#(obj_rent.rent_amount_base * 12) /  obj_rent.rent_total
		debug(res)
		return res
		
	def _rent_amount_years(self,cr,uid,ids,field_name,args,contexto):
		res = {}
		debug("=============================YEARS")
		for obj_rent in self.pool.get('rent.rent').browse(cr,uid,ids):
			debug(obj_rent)
			
			years_val = {}
			debug(valor)
			years_val['rent_rise_year2'] = obj_rent.rent_amount_base * (1 + obj_rent.rent_rise)
			years_val['rent_rise_year3'] = years_val['rent_rise_year2']  * (1 + obj_rent.rent_rise)
			res[obj_rent.id] = years_val
		debug(res)
		return res
	_columns = {
		'name'                  : fields.char('Name',size=64),
		'rent_rent_client'      : fields.many2one('res.partner','Client', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_end_date'         : fields.date('Ending Date', required=True, states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_ending_motif'     : fields.selection([('Desertion','Desertion'),('No Renovation','No Renovation'),('Eviction','Eviction')],'Ending Motif'),
		'rent_ending_motif_desc': fields.text('Ending Motif Description'),
		
		'rent_rise'             : fields.float('Anual Rise', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_amount_base'      : fields.float('Final Price $', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_performance'      : fields.function(_rent_performance, type='char',method = True,string='Performance'),
		#'rent_rate'             : fields.float('Anual Rise', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_rise_year2'       : fields.function(_rent_amount_years, type='float',method = True,string='Year 2 $', multi='Years'),
		'rent_rise_year3'       : fields.function(_rent_amount_years, type='float',method = True,string='Year 3 $', multi='Years'),
		'rent_amount_per_sqr'   : fields.function(_performance_per_sqr, type='float',method = True,string='Amount $'),
		
		'rent_type'             : fields.selection([('Contract','Contract'),('Adendum','Adendum'),('Renovation','Renovation')],'Type', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'state'                 : fields.selection([('valid','Valid'),('finished','Finished'),('draft','Draft')],'Status', readonly=True),
		'rent_start_date'       : fields.date('Starting Date', required=True, states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_total'            : fields.function(_get_total_rent,type='float',method=True,string='Total Paid'),
		'rent_rent_local'       : fields.many2one('rent.floor.local','Local', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_rent_parking'     : fields.many2one('rent.floor.parking','Parking', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_rent_estate'      : fields.many2one('rent.estate','Estate', states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_related_real'     : fields.selection([('local','Locals'),('parking','Parking'),('estate','Estates')],'Type of Real Estate', required=True,states={'valid':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_years'            : fields.function(_calculate_years,type='integer',method=True,string = 'Years' ,help='Check if you want to calculate a rent for locals'),
		'rent_modif'            : fields.one2many('rent.rent', 'rent_modif_ref','Contract reference', states={'draft':[('readonly',True)], 'finished':[('readonly',True)]}),
		'rent_modif_ref'        : fields.many2one('rent.rent', 'Modifications'),
		'currency_id'           : fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'rent_estimates'        : fields.one2many('rent.rent.estimate', 'estimate_rent','Estimates'),         
	}
	
	_defaults = {
		'state'        : 'draft',
		'rent_type'    : 'Contract',
		'currency_id': _get_currency,
	}
rent_rent()

class rent_rent_estimate(osv.osv):
	_name = 'rent.rent.estimate'
		
	def _performance_years(self,cr,uid,ids,field_name,args,context):
		res = {}
	#	debug("=============================ANOS")
		for obj_estimate in self.pool.get('rent.rent.estimate').browse(cr,uid,ids):
			res[obj_estimate.id] = 1 / (obj_estimate.estimate_performance / 100.00)
		return res
	def _performance_amount(self,cr,uid,ids,field_name,args,context):
		res = {}
		amount = 0
	#	debug("=============================amount")
		for obj_estimate in self.pool.get('rent.rent.estimate').browse(cr,uid,ids):
			obj_rent = obj_estimate.estimate_rent
	#		debug(obj_rent)
			amounts_val = {}
			
			currency_id = obj_rent.currency_id
			debug(currency_id)
			rate_cr = currency_id.rate
			rate_us = 1
						
			amounts_val['estimate_amountc'] = (obj_estimate.estimate_rent.rent_total * (obj_estimate.estimate_performance/100.00)  / 12) / rate_us
			amounts_val['estimate_amountd'] = (obj_estimate.estimate_rent.rent_total * (obj_estimate.estimate_performance/100.00)  / 12) * rate_cr
			res[obj_estimate.id] = amounts_val
	#	debug(res)
		return res
	def _performance_currency(self,cr,uid,ids,field_name,args,contexto):
		res = {}
	#	debug("=============================col")
		for obj_estimate in self.pool.get('rent.rent.estimate').browse(cr,uid,ids):
			obj_rent = obj_estimate.estimate_rent
	#		debug(obj_rent)
			
			currencies_val = {}
			valor = obj_rent._get_total_area(obj_rent.id,None,None)[obj_rent.id]
			debug(valor)
			currencies_val['estimate_colones'] = obj_estimate.estimate_amountc / valor
			currencies_val['estimate_dollars'] = obj_estimate.estimate_amountd / valor
			res[obj_estimate.id] = currencies_val
	#	debug(res)
		return res
	_columns = {
		'estimate_performance'       : fields.float('Performance',digits=(12,2), help='This a percentaje number'),
		'estimate_years'             : fields.function(_performance_years, type='float',method = True,string='Years'),
		'estimate_amountc'           : fields.function(_performance_amount, type='float',method = True,string='Amount', multi=True),
		'estimate_colones'           : fields.function(_performance_currency, type='float',method = True,string='c / m2',multi='Currency'),
		
		'estimate_amountd'           : fields.function(_performance_amount, type='float',method = True,string='Amount $', multi=True),
		'estimate_dollars'           : fields.function(_performance_currency, type='float',method = True,string='s / m2',multi='Currency'),
		
		'estimate_cust_colones'      : fields.integer('Amount c'),
		'estimate_cust_dollars'      : fields.integer('Amount s'),
		
		'estimate_dec_min_dollars'   : fields.integer('Amount s'),
		'estimate_dec_base_dollars'  : fields.integer('Amount s'),
		'estimate_rent'              : fields.many2one('rent.rent','Rent'),
		'estimate_date'              : fields.date('Fecha'),
		'estimate_state'             : fields.selection([('recommend','Recommend'),('min','Min'),('norec','Not Recomended')],'Status',readonly=True),
	}
rent_rent_estimate()

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
			obj_contract.write({'contract_clauses' : [(0,0,{'sequence':i,'rent_contract_id':obj_contract.id,'rent_contract_clause_id' : clause_perm})]})
			i+=1
		return obj_contract.id
				
	_columns = {
		'name'             : fields.char('Reference', size=64),
		'contract_rent'    : fields.many2one('rent.rent','Rent Reference'),
		'contract_clauses' : fields.one2many('rent.contract.clause.rel','rent_contract_id','Clausulas'),
		#'contract_clauses' : fields.many2many('rent.contract.clause','rent_contract_clause_rel','name','clause_code','Clausulas'),
		#'contract_design'  : fields.char('Design',size=64),
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
		'clause_is_basic' : fields.boolean('Priority', help = 'Check if the clause should allways appear on every contract you create'),
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
