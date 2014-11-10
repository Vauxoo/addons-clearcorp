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
#    This program is distributed in the hope that it will be useful,related relationrelated relation
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields, orm
import datetime

class ProductCodeHistory(osv.Model):
    _name = 'product.code.history'
    
    _columns={
                'product_id': fields.many2one('product.product',string="Product"),
                'datetime':fields.datetime(required=True,string="Date Time"),
                'default_code':fields.char(required=True,string="Default Code")
                }
    _defaults={
               'datetime':fields.datetime.now
               }
    
class product_template(osv.Model):
    _inherit = "product.template"
    
    _columns = {
        'code_history_ids': fields.related('product_variant_ids', 'code_history_ids', type='one2many', relation='product.code.history',string='Product Code History'),
              }
      
class Product(osv.Model):
    _inherit = 'product.product'
    
    _columns={
             'code_history_ids': fields.one2many('product.code.history','product_id',string="Product Code History"),
        }
    
    def name_search(self, cr, uid,name,args=None,operator='ilike', context=None,limit=100):
        history_obj = self.pool.get('product.code.history')
        if not args:
            args = []
        if name:
            ids = self.search(cr, uid, [['name','ilike',name]]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [['default_code','ilike',name]]+ args, limit=limit, context=context)
                if not ids:
                    history_ids = history_obj.search(cr, uid, [['default_code','ilike',name]]+ args, limit=limit, context=context)         
                    for product in history_obj.browse(cr,uid,history_ids,context=context):
                        ids=[product.product_id.id]
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        result = self.name_get(cr, uid, ids, context=context)
        return result

    def create(self, cr, uid, vals, context=None):
        new_product=super(Product, self).create(cr, uid, vals, context=context)
        history_obj = self.pool.get('product.code.history')
        default_code = vals.get('default_code', False)
        if default_code and default_code!='':
                new_history=history_obj.create(cr, uid,{'product_id':new_product,
               'default_code':default_code   
            }, context=context)
        
        return new_product
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(Product, self).write(cr, uid, ids, vals, context=context)
        history_obj = self.pool.get('product.code.history')
        default_code = vals.get('default_code', False)
        if default_code and  default_code!='':
                new_history=history_obj.create(cr, uid,{'product_id':ids[0],
               'default_code': default_code   
            }, context=context)
        return res
    