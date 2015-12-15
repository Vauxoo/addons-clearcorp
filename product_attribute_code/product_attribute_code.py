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


class product_attribute_value(models.Model):

    _inherit = 'product.attribute.value'

    product_code = fields.Char(string="Product Code", default='')


class product_category(models.Model):

    _inherit = 'product.category'

    product_code_from_attributes = fields.Boolean(
        string="Product Code From Attributes")


class product_template(models.Model):

    _inherit = 'product.template'

    @api.multi
    def update_product_attribute_code(self):
        attribute_value_obj = self.env['product.attribute.value']
        for template in self:
            for product in template.product_variant_ids:
                if product.categ_id.product_code_from_attributes:
                        attribute_ids = product.attribute_value_ids._ids
                        order_attributes_ids = attribute_value_obj.search(
                            [('id', 'in', attribute_ids)], order='sequence')
                        code = ""
                        for attribute in order_attributes_ids:
                            if attribute.product_code:
                                code += attribute.product_code
                        product.write({'default_code': code})
        return True


class product_product(models.Model):

    _inherit = 'product.product'

    def create(self, cr, uid, vals, context=None):
        attribute_value_obj = self.pool.get('product.attribute.value')
        if context is None:
            context = {}
        res = super(product_product, self).create(cr, uid, vals, context=None)
        product = self.browse(cr, uid, res, context=context)

        if product.categ_id.product_code_from_attributes and \
                ('default_code' in vals.keys() or not
                 product.default_code):
            if 'attribute_value_ids'in vals.keys():
                attribute_ids = vals['attribute_value_ids'][0][2]
                order_attributes_ids = attribute_value_obj.search(
                    cr, uid, [('id', 'in', attribute_ids)],
                    order="sequence")
                code = ""
                for attribute in attribute_value_obj.browse(
                        cr, uid, order_attributes_ids, context=context):
                    if attribute.product_code:
                        code += attribute.product_code
                self.write(cr, uid, product.id,
                           {'default_code': code}, context=context)
        return res
