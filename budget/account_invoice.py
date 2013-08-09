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

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    def _check_from_order(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = context.get('from_order', False)
        return res

    _columns= {
    'budget_move_id': fields.many2one('budget.move', 'Budget move', readonly=True, ),
    'from_order': fields.boolean('From order')
    }
    _defaults={
     'from_order': _check_from_order          
    }
    
    def create_budget_move(self,cr, uid, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        type=''
        
        if vals['type'] in ('in_invoice','out_refund'):
            type = 'manual_invoice_in'
        if vals['type'] in ('out_invoice','in_refund'):
            type = 'manual_invoice_out'
        move_id = bud_move_obj.create(cr, uid, { 'type':'invoice_out' }, context=context)
        return move_id
    
    def create(self, cr, uid, vals, context=None):
        order_id = None
        if not _check_from_order(cr, uid, context=context):
            obj_bud_move = self.pool.get('budget.move')
            move_id = self.create_budget_move(cr, uid, vals, context=context)
            vals['budget_move_id'] = move_id
            order_id =  super(sale_order, self).create(cr, uid, vals, context=context)
            for order in self.browse(cr,uid,[order_id], context=context):
                obj_bud_move.write(cr, uid, [move_id], {'origin': order.name }, context=context)
        else:
            order_id =  super(sale_order, self).create(cr, uid, vals, context=context)
        return order_id
    
    def write(self, cr, uid, ids, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        result = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            move_id = order.budget_move_id.id
            bud_move_obj.write(cr,uid, [move_id], {'date':order.budget_move_id.date},context=context)
        return result
    
class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    def _check_from_order(self, cr, uid, ids, field_name, args, context=None):
        result = False
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.invoice_id:
                res[line.id] = line.invoice_id.from_order
            else:
                res[line.id] = context.get('from_order', False)
        return res
    
    _columns= {
    'program_line_id': fields.many2one('budget.program.line', 'Program line', ),
    'invoice_from_order': fields.function(_check_from_order, type='boolean', method=True, string='From order',readonly=True, store=True),
    #'invoice_from_order': fields.related('invoice_id','from_order', string='From order'),
    }
    
    _defaults = {}
    
    def create_budget_move_line(self,cr, uid, vals, line_id, context=None):
        
        acc_inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        fixed_amount = 0.0
        inv_id = vals['invoice_id'] 
        invoice = acc_inv_obj.browse(cr, uid, [inv_id], context=context)[0]
        invoice_line = inv_line_obj.browse(cr, uid, [line_id], context=context)[0]
        move_id = invoice.budget_move_id.id
        
        if invoice.type in ('in_invoice','out_refund'):
            fixed_amount = invoice_line.price_subtotal
        if invoice.type in ('out_invoice','in_refund'):
            fixed_amount = invoice_line.price_subtotal * -1 #should be negative because it is an income
            
        bud_line_obj.create(cr, uid, {'budget_move_id': move_id,
                                         'origin' : invoice_line.name,
                                         'program_line_id': vals['program_line_id'], 
                                         'fixed_amount': fixed_amount , 
                                         'inv_line_id': line_id,
                                          }, context=context)
        return line_id
    
    def create(self, cr, uid, vals, context=None):
        line_id =  super(account_invoice_line, self).create(cr, uid, vals, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            if not line.invoice_id.from_order:
                self.create_budget_move_line(cr, uid, vals, line_id, context=context)
        return line_id
    
    def write(self, cr, uid, ids, vals, context=None):
        
        bud_line_obj = self.pool.get('budget.move.line')
        result = super(account_invoice_line, self).write(cr, uid, ids, vals, context=context) 
        for line in self.browse(cr, uid, ids, context=context):
            search_result = bud_line_obj.search(cr, uid,[('inv_line_id','=', line.id)], context=context) 
            bud_line_id = search_result[0]
            if bud_line_id:
                fixed_amount = 0.0
                if invoice.type in ('in_invoice','out_refund'):
                    fixed_amount = invoice_line.price_subtotal
                if invoice.type in ('out_invoice','in_refund'):
                    fixed_amount = invoice_line.price_subtotal * -1 
                
                bud_line_obj.write(cr, uid, [bud_line_id], {'program_line_id': line.program_line_id.id, 'fixed_amount':fixed_amount})
        return result