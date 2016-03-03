# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
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

from openerp.osv import osv,fields, orm
from openerp.tools.translate import _

class ProductCategory(osv.Model):
    _inherit = 'product.category'
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','code','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            code=record['code']
            if code:
                name=code + ' '+ name
            
            if record['parent_id']:
                name =record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
    
    def name_search(self, cr, uid,name,args=None,operator='ilike', context=None,limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, [['name','ilike',name]]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [['code','ilike',name]]+ args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        result = self.name_get(cr, uid, ids, context=context)
        return result

    
    _columns = {
                'code': fields.char(string="Code")
                }
    
    _sql_constraints = [
        ('code_unique',
        'UNIQUE(code)',
        'The code already exist')
                        ]