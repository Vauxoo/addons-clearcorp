# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp

class stock_move_analysis(osv.osv):
    _name = "stock.move.analysis"
    _description = "Stock Move Analysis"
    _auto = False

    def _compute_total(self, cr, uid, ids, name, arg=None, context=None):
        res = {}
        product_price_history_obj = self.pool.get('product.price.history')
        company_user_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        
        for stock_move in self.browse(cr, uid, ids, context=context):
            res[stock_move.id] = 0.0            
            #Result of standard_price is a dictionary, where keys are product_id and value in field_names, in this case, 'standard_price'
            standard_price = product_price_history_obj._get_historic_price(cr, uid, [stock_move.product_id.id], company_user_id, datetime=stock_move.date, field_names=['standard_price'])
            if standard_price[stock_move.product_id.id]['standard_price'] == 0:
                standard_price = self.pool.get('product.product').browse(cr, uid, stock_move.product_id.id).standard_price
                total = stock_move.product_qty * standard_price
            else:
                total = stock_move.product_qty * standard_price[stock_move.product_id.id]['standard_price']
            
            res[stock_move.id] = total
        
        return res
    
    def _compute_standard_price(self, cr, uid, ids, name,arg=None, context=None):
        res = {}
        product_price_history_obj = self.pool.get('product.price.history')
        company_user_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        
        for stock_move in self.browse(cr, uid, ids, context=context):
            res[stock_move.id] = 0.0             
            #Result of standard_price is a dictionary, where keys are product_id and value in field_names, in this case, 'standard_price'
            standard_price = product_price_history_obj._get_historic_price(cr, uid, [stock_move.product_id.id], company_user_id, datetime=stock_move.date, field_names=['standard_price'])
            if standard_price[stock_move.product_id.id]['standard_price'] == 0:
                standard_price = self.pool.get('product.product').browse(cr, uid, stock_move.product_id.id).standard_price            
            else:
                standard_price = standard_price[stock_move.product_id.id]['standard_price']
            
            res[stock_move.id] = standard_price
        
        return res

    _columns = {
        'date': fields.datetime('Date', readonly=True),
        'origin': fields.char('Description', readonly=True),
        'name': fields.char('Name', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'location_id': fields.many2one('stock.location', 'Source Location', readonly=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', readonly=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True),   
        'standard_price': fields.function(_compute_standard_price, digits_compute=dp.get_precision('Account'), string='Standard Price',readonly=True, type="float"),
        'total': fields.function(_compute_total, digits_compute=dp.get_precision('Account'), string='Total',readonly=True, type="float"),     
    }

    _order = 'date asc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_move_analysis')
        cr.execute("""
            create or replace view stock_move_analysis as (
            select
                sm.id as id,
                sm.date as date,
                sm.origin as origin,
                sm.name as name,
                sm.product_id as product_id,
                sm.location_id as location_id, 
                sm.location_dest_id as location_dest_id,
                sum(sm.product_qty) as product_qty
            from
                stock_move sm
                left join product_product p on (sm.product_id = p.id)
            group by sm.id, sm.date, sm.origin, sm.name, sm.product_id, sm.location_id, sm.location_dest_id
            )
        """)
        
stock_move_analysis()