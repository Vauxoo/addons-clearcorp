# -*- encoding: utf-8 -*-
##############################################################################
#
#    account_company_shortcut_rename.py
#    account_company_shortcut_rename
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

class account_account(osv.osv):
	_name = "account.account"
	_inherit = "account.account"
	
	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		res = []
		for obj_account in self.browse(cr,uid,ids):
			data = []
			account = obj_account.parent_id
			if account.parent_id:
				while account.parent_id:
					data.insert(0,(account.shortcut or account.name))
					account = account.parent_id
			data.append(obj_account.name)
			data = '/'.join(data)
			company = obj_account.company_id
			data = (company and company.shortcut + "-" or '')  + obj_account.code + ' ' + data
			res.append((obj_account.id, data))  
		return res
	
	def _complete_name(self, cr, uid, ids, name, args, context=None):
		""" Forms complete name of account from parent account to child account.
		@return: Dictionary of values
		"""
		res = {}
		name_list = self.name_get(cr,uid,ids,context)
		for name in name_list:
			res[name[0]] = name[1]
		return res
	_columns = {
		'complete_name': fields.function(_complete_name, method=True, type='char', size=100, string="Account Name"),
	}
account_account()

class res_company(osv.osv):
	_name = 'res.company'
	_inherit = 'res.company'
	_columns = {
		'shortcut'  : fields.char('Shortcut', size=8,help='Shortcut for the company, It would be added on some places as part of the name that will be shown'),
	}	
res_company()
