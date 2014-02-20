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
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns= {
    'budget_move_id': fields.many2one('budget.move', 'Budget move' )
    }
    
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        acc_inv_mov = self.pool.get('account.invoice')
        res = False
        for id in ids:
            context.update({'from_order' : True,})
            invoice_id = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context=context)
            acc_inv_mov.write(cr, uid, [invoice_id],{'from_order': True})
            for sale in self.browse(cr, uid, [id],context=context):
                move_id = sale.budget_move_id.id
                obj_bud_mov.action_execute(cr,uid, [move_id],context=context)
                res = invoice_id
        return res
    
    def create_budget_move(self,cr, uid, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        move_id = bud_move_obj.create(cr, uid, { 'type':'invoice_out' }, context=context)
        return move_id
    
    def create(self, cr, uid, vals, context=None):
        obj_bud_move = self.pool.get('budget.move')
        move_id = self.create_budget_move(cr, uid, vals, context=context)
        vals['budget_move_id'] = move_id
        order_id =  super(sale_order, self).create(cr, uid, vals, context=context)
        for order in self.browse(cr,uid,[order_id], context=context):
            obj_bud_move.write(cr, uid, [move_id], {'origin': order.name }, context=context)
        return order_id
    
    def write(self, cr, uid, ids, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        result = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            move_id = order.budget_move_id.id
            bud_move_obj.write(cr,uid, [move_id], {'date':order.budget_move_id.date},context=context)
        return result
    
class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'   

    def _subtotal_discounted_taxed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context): 
            if line.discount > 0:
                price_unit_discount = line.price_unit - (line.price_unit * (line.discount / 100) )
            else:
                price_unit_discount = line.price_unit
            #-----taxes---------------# 
            #taxes must be calculated with unit_price - discount
            amount_discounted_taxed = self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, price_unit_discount, line.product_uom_qty, line.product_id.id, line.order_id.partner_id)['total_included']
            res[line.id]= amount_discounted_taxed
        return res
                                
    _columns = {    
    'program_line_id': fields.many2one('budget.program.line', 'Program line', required=True),
    'subtotal_discounted_taxed': fields.function(_subtotal_discounted_taxed, digits_compute= dp.get_precision('Account'), string='Subtotal', ),
    }
    
    def create_budget_move_line(self,cr, uid, vals, line_id, context=None):
        
        sale_order_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        
        so_id = vals['order_id'] 
        order = sale_order_obj.browse(cr, uid, [so_id], context=context)[0]
        order_line = sale_line_obj.browse(cr, uid, [line_id], context=context)[0]
        move_id = order.budget_move_id.id
        bud_line_obj.create(cr, uid, {'budget_move_id': move_id,
                                         'origin' : order_line.name,
                                         'program_line_id': vals['program_line_id'], 
                                         'fixed_amount': order_line.subtotal_discounted_taxed * -1 , #should be negative because it is an income
                                         'so_line_id': line_id,
                                          }, context=context)
        return line_id
    
    def create(self, cr, uid, vals, context=None):
        line_id =  super(sale_order_line, self).create(cr, uid, vals, context=context)
        self.create_budget_move_line(cr, uid, vals, line_id, context=context)
        return line_id
#    
    def write(self, cr, uid, ids, vals, context=None):
        
        bud_line_obj = self.pool.get('budget.move.line')
        result = super(sale_order_line, self).write(cr, uid, ids, vals, context=context) 
        for line in self.browse(cr, uid, ids, context=context):
            search_result = bud_line_obj.search(cr, uid,[('so_line_id','=', line.id)], context=context) 
            bud_line_id = search_result[0]
            if bud_line_id:
                bud_line_obj.write(cr, uid, [bud_line_id], {'program_line_id': line.program_line_id.id, 'fixed_amount':line.subtotal_discounted_taxed})
        return result  