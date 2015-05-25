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

from openerp import models, fields, api

class productProductinherit(models.Model):

     _inherit = 'product.product'
     
     ir_sequence_id = fields.Many2one('ir.sequence', relation='categ_id.ir_sequence_cat_id', store=True, string="Product Sequence")
     
      #'categ_id', 'ir_sequence_cat_id', 

     #Change sequence. It depends of category assigned to product
     @api.onchange('ir_sequence_id')
     def onchange_categ_id(self):
         if self.categ_id:
             cat_obj = self.env['product.category'].browse(self.categ_id.id)
             if cat_obj.ir_sequence_cat_id:
                 return {'value': {'ir_sequence_id': cat_obj.ir_sequence_cat_id.id}}
             else:
                 return {'value': {'ir_sequence_id': False}}
         return {'value': {'ir_sequence_id': False}}

     #Redefine create. To new products, assign new default code, this depends of sequence in
     @api.model
     def create(self, values):
         seq_obj = self.env['ir.sequence']
         if 'default_code' not in values.keys() or ('default_code' in values.keys() and not values['default_code']):
             if 'categ_id' in values.keys():
                 categ_obj = self.env['product.category'].browse(values['categ_id'])
                 if categ_obj.ir_sequence_cat_id:
                     default_code = seq_obj.next_by_id(categ_obj.ir_sequence_cat_id.id)
                     values['default_code'] = default_code
         res = super(productProductinherit, self).create(values)
         return res
