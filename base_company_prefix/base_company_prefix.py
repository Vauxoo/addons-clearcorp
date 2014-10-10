# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by ClearCorp S.A.
#    Copyright (C) 2009-TODAY ClearCorp S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
import os

class res_company(orm.Model):
    _name = "res.company"
    _inherit = 'res.company'
    _order = 'prefix'
    _columns = {
        'prefix' : fields.char('Prefix', size=10),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for obj_company in self.browse(cr, uid, ids, context=context):
            obj_company_name = obj_company.prefix and obj_company.prefix + ' '  or ''
            obj_company_name += obj_company.name
            res.append((obj_company.id,obj_company_name))
        return res
