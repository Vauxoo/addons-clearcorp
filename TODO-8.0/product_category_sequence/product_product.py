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

from openerp.osv import fields, osv, orm

class productProductinherit(orm.Model):
    
     _inherit = 'product.product'
     _columns = {
        'ir_sequence_id': fields.related('categ_id', 'ir_sequence_cat_id', type="many2one", relation="ir.sequence", store=True, string="Product Sequence"),                 
     }
     
     #Change sequence. It depends of category assigned to product
     def onchange_categ_id(self, cr, uid, ids, categ_id, context=None):
         if categ_id:
             cat_obj = self.pool.get('product.category').browse(cr, uid, categ_id, context=context)
             if cat_obj.ir_sequence_cat_id:
                 return {'value': {'ir_sequence_id': cat_obj.ir_sequence_cat_id.id}}
             else:
                 return {'value': {'ir_sequence_id': False}}
             
         return {'value': {'ir_sequence_id': False}}
     
     #Redefine create. To new products, assign new default code, this depends of sequence in 
     def create(self, cr, uid, vals, context={}):
         seq_obj = self.pool.get('ir.sequence')
         
         if 'default_code' not in vals.keys() or ('default_code' in vals.keys() and not vals['default_code']):
             if 'categ_id' in vals.keys():
                 categ_obj = self.pool.get('product.category').browse(cr, uid, vals['categ_id'], context=context)
                 if categ_obj.ir_sequence_cat_id:
                     default_code = seq_obj.next_by_id(cr, uid, categ_obj.ir_sequence_cat_id.id, context=context)
                     vals['default_code'] = default_code
         
         res = super(productProductinherit, self).create(cr, uid, vals, context)
         return res
         
         