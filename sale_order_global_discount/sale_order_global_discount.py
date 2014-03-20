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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import pooler
from osv import fields, osv
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _description = 'Order Line'
    
    def _amount_line_no_discount(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'price_subtotal_not_discounted': fields.function(_amount_line_no_discount, digits_compute= dp.get_precision('Account'), string='Subtotal',
            store = {
                'sale.order.line': (lambda self, cr, uid, ids, c={}: ids, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 5),
            }),
    }
    
    def button_dummy(self, cr, uid, ids, context=None):
        #To recalculate function fields
        for line in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [line.id], {'id': line.id}, context=context)
        return True
    
class SaleOrder(osv.osv):
    _inherit = 'sale.order'
    _description = 'Sales Order'
    
    def _amount_line_tax_no_discount(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        ###Workaround, functional fields###
        ###See sale.order###
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'order_discount': 0.0,
                'amount_discounted': 0.0,
                'amount_untaxed_not_discounted': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                res[order.id]['amount_untaxed_not_discounted'] += line.price_subtotal_not_discounted
                res[order.id]['amount_discounted'] += line.price_subtotal_not_discounted - line.price_subtotal
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']        
            if res[order.id]['amount_untaxed_not_discounted'] == 0:
                res[order.id]['order_discount'] = 0
            else:
                res[order.id]['order_discount'] = 100 * res[order.id]['amount_discounted'] / res[order.id]['amount_untaxed_not_discounted']
        return res
    
    def _get_order_ccorp(self, cr, uid, ids, context=None):
        return self.pool.get('sale.order')._get_order(cr, uid, ids, context)
        
    _columns = {
        'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order_ccorp, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax."),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order_ccorp, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount.", track_visibility='always'),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order_ccorp, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'order_discount': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order_ccorp, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums'),
        'amount_discounted': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Discount',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order_ccorp, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums'),
        'amount_untaxed_not_discounted': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Subtotal',
            store = {
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order_ccorp, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums'),
                }
        
    def button_dummy(self, cr, uid, ids, context={}):
        if context is None:
            context = {}
        #To recalculate function fields
        if isinstance(ids, int):
            ids = [ids]
        for sale in self.browse(cr, uid, ids, context=context):
            context.update({'second_time': True})
            self.write(cr, uid, [sale.id], {}, context=context)
        super(SaleOrder, self).button_dummy(cr, uid, ids, context=context)
        return True
    
    def create(self, cr, uid, vals, context=None):
        sale_id = super(SaleOrder, self).create(cr, uid, vals, context=context)
        self.button_dummy(cr, uid, [sale_id], context=context)
        return sale_id
    
    def write(self, cr, uid, ids, vals, context={}):
        if context is None:
            context = {}
        if 'second_time' not in context:
             self.button_dummy(cr, uid, ids, context=context)
        else:
            del context['second_time']
        return super(SaleOrder, self).write(cr, uid, ids, vals, context=context)
