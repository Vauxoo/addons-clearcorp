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
