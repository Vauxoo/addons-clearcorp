# -*- encoding: utf-8 -*-
##############################################################################
#
#    stock_location_rename.py
#    stock_location_rename
#    First author: Mag Guevara <mag.guevara@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2011-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without modification, are
#    permitted provided that the following conditions are met:
#    
#       1. Redistributions of source code must retain the above copyright notice, this list of
#          conditions and the following disclaimer.
#    
#       2. Redistributions in binary form must reproduce the above copyright notice, this list
#          of conditions and the following disclaimer in the documentation and/or other materials
#          provided with the distribution.
#    
#    THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ``AS IS'' AND ANY EXPRESS OR IMPLIED
#    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#    
#    The views and conclusions contained in the software and documentation are those of the
#    authors and should not be interpreted as representing official policies, either expressed
#    or implied, of ClearCorp S.A..
#    
##############################################################################
from osv import osv, fields
from tools import debug
from tools.translate import _

class stock_location(osv.osv):
	_name = "stock.location"
	_inherit = "stock.location"
	
	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		res = []
		for obj_stock_location in self.browse(cr,uid,ids):
			data = []
			location = obj_stock_location.location_id
			while location:
				data.insert(0,(location.shortcut or location.name))
				location = location.location_id
			data.append(obj_stock_location.name)
			data = '/'.join(data)
			res.append((obj_stock_location.id, data))  
		return res
	
	def _complete_name2(self, cr, uid, ids, name, args, context=None):
		""" Forms complete name of location from parent location to child location.
		@return: Dictionary of values
		"""
		res = {}
		name_list = self.name_get(cr,uid,ids,context)
		for name in name_list:
			res[name[0]] = name[1]
		return res
	_columns = {
		'shortcut'  :  fields.char('Shortcut',size=10),
		'complete_name': fields.function(_complete_name2, method=True, type='char', size=100, string="Location Name"),
	}
stock_location()
