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
import decimal_precision as dp

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
    
#    def create_budget_move(self,cr, uid, vals, context=None):
#        bud_move_obj = self.pool.get('budget.move')
#        type=''
#        
#        if context.get('type',"") in ('in_invoice','out_refund'):
#            type = 'manual_invoice_in'
#        if context.get('type',"") in ('out_invoice','in_refund'):
#            type = 'manual_invoice_out'
#        move_id = bud_move_obj.create(cr, uid, { 'type': type }, context=context)
#        return move_id

    def create_budget_move(self,cr, uid, ids, context=None):
        bud_move_obj = self.pool.get('budget.move')
        acc_inv_obj = self.pool.get('account.invoice')
        for invoice in acc_inv_obj.browse(cr, uid, ids, context=context):
            if invoice.type in ('in_invoice','out_refund'):
                type = 'manual_invoice_in'
            if invoice.type in ('out_invoice','in_refund'):
                type = 'manual_invoice_out'
        move_id = bud_move_obj.create(cr, uid, { 'type': type }, context=context)
        return move_id

    
    def create_budget_move_line(self,cr, uid, line_id, context=None):    
        acc_inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        fixed_amount = 0.0
        invoice_line = inv_line_obj.browse(cr, uid, [line_id], context=context)[0]
        invoice = acc_inv_obj.browse(cr, uid, [invoice_line.invoice_id.id], context=context)[0]
        move_id = invoice.budget_move_id.id
        
        if invoice.type in ('in_invoice','out_refund'):
            fixed_amount = invoice_line.subtotal_discounted_taxed
        if invoice.type in ('out_invoice','in_refund'):
            fixed_amount = invoice_line.subtotal_discounted_taxed * -1 #should be negative because it is an income
            
        bud_line_obj.create(cr, uid, {'budget_move_id': move_id,
                                         'origin' : invoice_line.name,
                                         'program_line_id': invoice_line.program_line_id.id, 
                                         'fixed_amount': fixed_amount , 
                                         'inv_line_id': line_id,
                                          }, context=context)
        return line_id
 
    
#    def create(self, cr, uid, vals, context=None):
#        order_id = None
#        if not self._check_from_order(cr, uid, context=context):
#            obj_bud_move = self.pool.get('budget.move')
#            move_id = self.create_budget_move(cr, uid, vals, context=context)
#            vals['budget_move_id'] = move_id
#            order_id =  super(account_invoice, self).create(cr, uid, vals, context=context)
#            for order in self.browse(cr,uid,[order_id], context=context):
#                for line in order.invoice_line:
#                    if not line.invoice_id.from_order:
#                        self.create_budget_move_line(cr, uid, line.id, context=context)
#            obj_bud_move.write(cr, uid, [move_id], {'origin': order.name , 'fixed_amount':order.amount_total}, context=context)
#        else:
#            order_id =  super(account_invoice, self).create(cr, uid, vals, context=context)
#        return order_id
    
#    def write(self, cr, uid, ids, vals, context=None):
#        bud_move_obj = self.pool.get('budget.move')
#        bud_line_obj = self.pool.get('budget.move.line')
#        result = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
#        for order in self.browse(cr, uid, ids, context=context):
#            move_id = order.budget_move_id.id
#            for line in order.invoice_line:
#                search_result = bud_line_obj.search(cr, uid,[('inv_line_id','=', line.id)], context=context) 
#                if search_result:
#                    bud_line_id = search_result[0]
#                    fixed_amount = 0.0
#                    if order.type in ('in_invoice','out_refund'):
#                        fixed_amount = line.subtotal_discounted_taxed
#                    if order.type in ('out_invoice','in_refund'):
#                        fixed_amount = line.subtotal_discounted_taxed * -1
#                    bud_line_obj.write(cr, uid, [bud_line_id], {'program_line_id': line.program_line_id.id, 'fixed_amount':fixed_amount})
#                else:
#                    self.create_budget_move_line(cr, uid, line.id, context=context)
#            if move_id:
#                bud_move_obj.write(cr,uid, [move_id], {'date':order.budget_move_id.date, 'fixed_amount':order.amount_total},context=context)
#        return result
#    
      
#    def invoice_validate(self, cr, uid, ids, context=None):
#        line_obj = self.pool.get('account.invoice.line')
#        bud_move_obj = self.pool.get('budget.move')
#        for invoice in self.browse(cr, uid, ids, context=context):
#            bud_move_obj.action_in_execution(cr, uid, [invoice.budget_move_id.id],context=context )
#        return super(account_invoice,self).invoice_validate(cr, uid, ids, context=context)
#    
    def invoice_validate(self, cr, uid, ids, context=None):
        obj_bud_move = self.pool.get('budget.move')
        if not self._check_from_order(cr, uid, context=context):    
            for order in self.browse(cr,uid,ids, context=context):
                move_id = self.create_budget_move(cr, uid, ids, context=context)
                self.write(cr, uid, [order.id], {'budget_move_id' :move_id }, context=context)
                for line in order.invoice_line:
                    if not line.invoice_id.from_order:
                        self.create_budget_move_line(cr, uid, line.id, context=context)
                obj_bud_move.write(cr, uid, [move_id], {'origin': order.name , 'fixed_amount':order.amount_total, 'arch_compromised':order.amount_total}, context=context)
                obj_bud_move.action_in_execution(cr, uid, [order.budget_move_id.id],context=context )
        return super(account_invoice,self).invoice_validate(cr, uid, ids, context=context)    
    
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
    
    def on_change_program_line(self, cr, uid, ids, program_line, context=None):
        for line in self.pool.get('budget.program.line').browse(cr, uid,[program_line], context=context):
            return {'value': {'line_available':line.available_budget},}
        return {'value': {}}
    
    def on_change_account_id(self, cr, uid, ids, account_id, context=None):
        if account_id:
            for account in self.pool.get('account.account').browse(cr, uid,[account_id], context=context):
                if account.default_budget_program_line.id:
                    return {'value': {'program_line_id':account.default_budget_program_line.id},}
        return {'value': {}}
    
    def _subtotal_discounted_taxed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context): 
            if line.discount > 0:
                price_unit_discount = line.price_unit - (line.price_unit * (line.discount / 100) )
            else:
                price_unit_discount = line.price_unit
            #-----taxes---------------# 
            #taxes must be calculated with unit_price - discount
            amount_discounted_taxed = self.pool.get('account.tax').compute_all(cr, uid, line.invoice_line_tax_id, price_unit_discount, line.quantity, line.product_id.id, line.invoice_id.partner_id)['total_included']
            res[line.id]= amount_discounted_taxed
        return res
    
    
    _columns= {
    'program_line_id': fields.many2one('budget.program.line', 'Program line', ),
    'invoice_from_order': fields.function(_check_from_order, type='boolean', method=True, string='From order',readonly=True, store=True),
    'line_available':fields.float('Line available',digits_compute=dp.get_precision('Account'),readonly=True),
    'subtotal_discounted_taxed': fields.function(_subtotal_discounted_taxed, digits_compute= dp.get_precision('Account'), string='Subtotal', ),
    }
    
    _defaults = {}
    
    def write(self, cr, uid, ids, vals, context=None):
        inv_obj = self.pool.get('account.invoice')
        result = super(account_invoice_line, self).write(cr, uid, ids, vals, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            inv_obj.write(cr, uid, [line.invoice_id.id], {'name':line.invoice_id.name },context=context)
        