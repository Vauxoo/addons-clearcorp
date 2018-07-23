
# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Addons modules by CLEARCORP S.A.
# Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,related relationrelated relation
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api,models,fields

class ResPartner(models.Model):
	_inherit = 'res.partner'
	
	@api.model
	def name_search(self,name, args=None, operator='ilike', limit=100):
		res = super(ResPartner, self).name_search(name, args = args, operator = 'ilike')
		recs = self.browse()
		recs=self.search([('trade_name', operator, name)] + args,
							  limit=limit)
		res = list(set(res + recs.name_get()))
		return res
		
	trade_name= fields.Char('Trade Name', size=128, help="Is used if the contact used trade name, and this is different to the business name")