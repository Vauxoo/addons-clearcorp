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


class product_product(osv.osv):
    _inherit = "product.product"
    def _get_currency(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for order in self.browse(cr, uid, ids):
            res[order.id] = 0
            for oline in order.order_line:
                res[order.id] += oline.price_unit * oline.product_qty
        return res

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        res = {}
        new_args = []
        cont=0

        if not args:
            args = []
        number_params = len(args)

        while cont<number_params:
            param=args[cont]
            if ('part_number' in param) or ('default_code' in param) or ('name' in param):
                search_vals = param[2].split()
                for val in search_vals:
                    new_args = new_args + [[param[0],'ilike', val]]

            cont = cont +1
        if len(new_args) > 0:
            args = new_args

        res = super(product_product, self).search(cr, uid, args, offset, limit, order, context, count)

        return res



    def _product_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        quantity = context.get('quantity') or 1.0
        pricelist = context.get('pricelist', False)
        if pricelist:
            for id in ids:
                try:
                    price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist], id, quantity, context=context)[pricelist]
                except:
                    price = 0.0
                res[id] = price
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def _product_partner_ref(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for p in self.browse(cr, uid, ids, context=context):
            data = self._get_partner_code_name(cr, uid, [], p, context.get('partner_id', None), context=context)
            if not data['code']:
                data['code'] = p.code
            if not data['name']:
                data['name'] = p.name
            res[p.id] = (data['code'] and ('['+data['code']+'] ') or '') + \
                    (data['name'] or '')
        return res

    _columns = {
        'currency_id': fields.many2one('res.currency','Currency'),
        'part_number': fields.char('Part Number', size=90),
        'default_code' : fields.char('Reference', size=64, select=True),
        'import_ok': fields.boolean('Could be imported'),
        'cost_fob': fields.float('Cost FOB o Ex Works'),
        'fob_currency_id': fields.many2one('res.currency','FoB Currency'),
    }
    _sql_constraints = [
        ('default_code_uniq', 'unique (default_code)', 'El code must be unique!')
    ]
    _defaults = {
        'import_ok': lambda *a: 1,
    }


    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}

        if 'currency_id' in context:
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field','=',ptype)])[0]
            price_type_currency_id = pricetype_obj.browse(cr,uid,price_type_id).currency_id.id

        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = product[ptype] or 0.0
            if ptype == 'list_price':
                res[product.id] = (res[product.id] * (product.price_margin or 1.0)) + \
                        product.price_extra
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, res[product.id], context['uom'])
            if 'currency_id' in context:
                res[product.id] = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                    context['currency_id'], res[product.id],context=context)

        return res

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [['default_code','ilike',name]]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [['part_number','ilike',name]]+ args, limit=limit, context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [['default_code',operator,name]], limit=limit, context=context))
                if len(ids) < limit:
                    ids.update(self.search(cr, user, args + [['name',operator,name]], limit=(limit-len(ids)), context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

product_product()


