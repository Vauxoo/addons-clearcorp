# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Frank Carvajal
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

from osv import fields, osv, orm
import os
import tools

class res_company(orm.Model):
    _name = "res.company"
    _description = 'Companies'
    _inherit = 'res.company'
    _order = 'prefix'
    _columns = {
        'prefix' : fields.char('Prefijo',size=10),
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

res_company()
