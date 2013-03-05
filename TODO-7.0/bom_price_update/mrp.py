# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by SIESA
#    Copyright (C) 2009-TODAY Soluciones Industriales Electromecanicas S.A. (<http://siesacr.com>).
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

from osv import osv, fields
import decimal_precision as dp
import math
import logging
import re
from tools.translate import _

class mrp_bom(osv.osv):
    _inherit ='mrp.bom'
    def create(self, cr, uid, vals, context=None):
        res = super(mrp_bom, self).create(cr, uid, vals, context)
        part_obj = self.pool.get('res.partner')
        bom = self.pool.get('mrp.bom').browse(cr, uid, res, context=context)
        product = bom.product_id
        standard_price = 0
        list_price = 0

        for line in bom.bom_lines:
            standard_price = standard_price + line.product_id.standard_price * line.product_qty
            list_price = list_price + line.product_id.list_price * line.product_qty
        standard_price = standard_price / bom.product_qty
        list_price = list_price / bom.product_qty

        if standard_price >0 and list_price >0:
            product.write({'standard_price': standard_price}, context=context)
            product.write({'list_price': list_price}, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(mrp_bom, self).write(cr, uid, ids, vals, context=context)
        bom_obj = self.pool.get('mrp.bom')
        prod_obj = self.pool.get('mrp.production')
        list_bom = self.pool.get('mrp.bom').browse(cr, uid, ids, context=context)
        prods_ids = prod_obj.search(cr, uid, [('bom_id','in',ids),('state','in',['confirmed','ready','in_production'])], context=context)
        standard_price = 0
        list_price = 0


        for bom in list_bom:
            new_prods = []
            product = bom.product_id

            for line in bom.bom_lines:
                standard_price = standard_price + line.product_id.standard_price * line.product_qty
                list_price = list_price + line.product_id.list_price * line.product_qty
            standard_price = standard_price / bom.product_qty
            list_price = list_price / bom.product_qty

            if standard_price >0 and list_price >0:
                product.write({'standard_price': standard_price}, context=context)
                product.write({'list_price': list_price}, context=context)


        return res

mrp_bom()
