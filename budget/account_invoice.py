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
import netsvc
import decimal_precision as dp

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    def _check_from_order(self, cr, uid, context=None, ids=None):
        if context is None:
            context = {}
            res = False
        if ids:
            for invoice in self.browse(cr, uid, ids, context=context):
                return invoice.from_order
        else:
            res = context.get('from_order', False)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.budget_move_id:
                invoice.budget_move_id._workflow_signal('button_cancel', context=context)
        return res

    def action_cancel_draft(self, cr, uid, ids, *args):
        res = super(account_invoice, self).action_cancel_draft(cr, uid, ids, *args)
        for invoice in self.browse(cr, uid, ids):
            if invoice.budget_move_id:
                invoice.budget_move_id._workflow_signal('button_draft')
        return res

    _columns= {
    'budget_move_id': fields.many2one('budget.move', 'Budget move', readonly=True, ),
    'from_order': fields.boolean('From order')
    }
    _defaults={
     'from_order': _check_from_order
    }


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

    def update_budget_move(self,cr, uid, ids, context=None):
        bud_move_obj = self.pool.get('budget.move')
        acc_inv_obj = self.pool.get('account.invoice')
        for invoice in acc_inv_obj.browse(cr, uid, ids, context=context):
            if invoice.type in ('in_invoice','out_refund'):
                type = 'manual_invoice_in'
            if invoice.type in ('out_invoice','in_refund'):
                type = 'manual_invoice_out'
            invoice.budget_move_id.write({ 'type': type}, context=context)
            move_ids = [(2, x.id)for x in invoice.budget_move_id.move_lines]
            if move_ids:
                invoice.budget_move_id.write({'move_lines': move_ids}, context=context)

    
    def create_budget_move_line_from_invoice(self, cr, uid, line_id, is_tax=False, context=None):    
        acc_inv_obj = self.pool.get('account.invoice')
        acc_move_obj = self.pool.get('account.move')
        inv_line_obj = self.pool.get('account.invoice.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        fixed_amount = 0.0
        
        invoice_line = inv_line_obj.browse(cr, uid, [line_id], context=context)[0]
        invoice = acc_inv_obj.browse(cr, uid, [invoice_line.invoice_id.id], context=context)[0]
        
        move_id = invoice.budget_move_id.id
        refund = False
        budget_type = ""
        vals = {'budget_move_id': move_id,
                                         'origin' : invoice_line.name,
                                         'program_line_id': invoice_line.program_line_id.id,
                                         'account_move_id': invoice.move_id.id
                                          }
        
        if invoice.type in ('in_invoice', 'out_refund'):
            fixed_amount = invoice_line.price_subtotal
            vals['inv_line_id']= line_id
            if invoice.type == 'out_refund':
                refund = True
        if invoice.type in ('out_invoice', 'in_refund'):
            fixed_amount = invoice_line.price_subtotal *-1  # should be negative because it is an income
            vals['inv_line_id']= line_id
            if invoice.type == 'in_refund':
                refund = True
        vals['fixed_amount']=fixed_amount
        
        bud_line = bud_line_obj.create(cr, uid, vals, context=context)
        
        if refund :
            budget_type = 'void'
        else:
            budget_type = 'budget'
        
        acc_move_obj.write(cr , uid, [invoice.move_id.id], {'budget_type': budget_type}, context=context)
        
        return bud_line
 
 ##
    def create_budget_move_line_from_tax(self, cr, uid, line_id, context=None):
        acc_inv_obj = self.pool.get('account.invoice')
        acc_inv_tax_obj = self.pool.get('account.invoice.tax')
        acc_move_obj = self.pool.get('account.move')
        inv_line_obj = self.pool.get('account.invoice.line')
        bud_move_obj = self.pool.get('budget.move')
        bud_line_obj = self.pool.get('budget.move.line')
        fixed_amount = 0.0
        tax_line = acc_inv_tax_obj.browse(cr, uid, [line_id], context=context)[0]
        invoice = acc_inv_obj.browse(cr, uid, [tax_line.invoice_id.id], context=context)[0]
        move_id = invoice.budget_move_id.id
        refund = False
        budget_type = ""
        vals = {'budget_move_id': move_id,
                                         'origin' : tax_line.name,
                                         'account_move_id': invoice.move_id.id
                                          }
        if invoice.type in ('in_invoice', 'out_refund'):
            fixed_amount = tax_line.tax_amount
            vals['tax_line_id']=line_id
            if invoice.type == 'out_refund':
                refund = True
        if invoice.type in ('out_invoice', 'in_refund'):
            fixed_amount = tax_line.tax_amount *-1
            vals['tax_line_id']= line_id
            if invoice.type == 'in_refund':
                refund = True
        invoice_lines = tax_line.invoice_id.invoice_line
        
        for inv_line in invoice_lines:
            if tax_line.base_amount == inv_line.price_subtotal:
                vals['program_line_id'] = inv_line.program_line_id.id
        
        vals['fixed_amount']=fixed_amount
        bud_line = bud_line_obj.create(cr, uid, vals, context=context)
        if refund :
            budget_type = 'void'
        else:
            budget_type = 'budget'
        
        acc_move_obj.write(cr , uid, [invoice.move_id.id], {'budget_type': budget_type}, context=context)
        
        return bud_line
 ##
 
    def invoice_validate(self, cr, uid, ids, context=None):
        obj_bud_move = self.pool.get('budget.move')
        obj_bud_move_line = self.pool.get('budget.move.line')
        validate_result = super(account_invoice,self).invoice_validate(cr, uid, ids, context=context)
        if not self._check_from_order(cr, uid, context=context, ids=ids):
            for order in self.browse(cr,uid,ids, context=context):
                if not order.budget_move_id:
                    move_id = self.create_budget_move(cr, uid, ids, context=context)
                else:
                    move_id = order.budget_move_id.id
                    self.update_budget_move(cr, uid, [order.id], context=context)
                self.write(cr, uid, [order.id], {'budget_move_id' :move_id }, context=context)
                #creating budget move lines per invoice line
                for line in order.invoice_line:
                    if not line.invoice_id.from_order:
                        created_line_id = self.create_budget_move_line_from_invoice(cr, uid, line.id, context=context)
                
                #creating budget move lines per tax line
                for line in order.tax_line:
                    if not line.invoice_id.from_order:
                        created_line_id = self.create_budget_move_line_from_tax(cr, uid, line.id, context=context)
                        
                obj_bud_move.write(cr, uid, [move_id], {'origin': order.name , 'fixed_amount':order.amount_total, 'arch_compromised':order.amount_total}, context=context)
                
                #Associating 
                bud_lines_ids = obj_bud_move_line.search(cr, uid, [('budget_move_id','=', move_id)], context=context)
                bud_lines = obj_bud_move_line.browse(cr, uid, bud_lines_ids, context=context)
                move_lines = order.move_id.line_id
                assigned_mov_lines= []
                
                for bud_line in bud_lines:
                    for move_line in move_lines:
                        fixed_amount = abs(move_line.debit - move_line.credit) or abs(move_line.amount_currency)
                        account_id = 0
                        if bud_line.inv_line_id and bud_line.inv_line_id.account_id:
                            account_id = bud_line.inv_line_id.account_id.id
                        elif bud_line.tax_line_id and bud_line.tax_line_id.account_id:
                            account_id = bud_line.tax_line_id.account_id.id
                            
                        if move_line.id not in assigned_mov_lines and bud_line.origin.find(move_line.name) != -1 and bud_line.fixed_amount == fixed_amount and \
                            account_id == move_line.account_id.id :
                            obj_bud_move_line.write(cr, uid, [bud_line.id],{'move_line_id':move_line.id})
                            assigned_mov_lines.append(move_line.id)
                
                obj_bud_move._workflow_signal(cr, uid, [move_id], 'button_execute', context=context)
        else:
            for invoice in self.browse(cr,uid,ids, context=context):
                for inv_line in invoice.invoice_line:
                    bud_line_id = obj_bud_move_line.search(cr,uid, [('inv_line_id', '=', inv_line.id)], context=context)
                    bud_line = obj_bud_move_line.browse(cr, uid, bud_line_id, context = context)[0]
                    move_id = bud_line.budget_move_id.id
                    move_lines = invoice.move_id.line_id
                    assigned_mov_lines = []
                    
                    for move_line in move_lines:
                        fixed_amount = abs(move_line.debit - move_line.credit) or abs(move_line.amount_currency)
                        account_id = 0
                        if bud_line.inv_line_id and bud_line.inv_line_id.account_id:
                            account_id = bud_line.inv_line_id.account_id.id
                        elif bud_line.tax_line_id and bud_line.tax_line_id.account_id:
                            account_id = bud_line.tax_line_id.account_id.id
                            
                        if move_line.id not in assigned_mov_lines and bud_line.fixed_amount == fixed_amount and \
                            account_id == move_line.account_id.id :
                            obj_bud_move_line.write(cr, uid, [bud_line.id],{'move_line_id':move_line.id})
                            assigned_mov_lines.append(move_line.id)
                
                obj_bud_move._workflow_signal(cr, uid, [move_id], 'button_execute', context=context)
                    
        return validate_result
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'budget_move_id': False})
        return super(account_invoice, self).copy(cr, uid, id, default, context=context)
    
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
    'invoice_from_order': fields.function(_check_from_order, type='boolean', method=True, string='From order',readonly=True,),
    'line_available':fields.float('Line available',digits_compute=dp.get_precision('Account'),readonly=True),
    'subtotal_discounted_taxed': fields.function(_subtotal_discounted_taxed, digits_compute= dp.get_precision('Account'), string='Subtotal', ),
    }
    
    _defaults = {}
    
    def write(self, cr, uid, ids, vals, context=None):
        inv_obj = self.pool.get('account.invoice')
        result = super(account_invoice_line, self).write(cr, uid, ids, vals, context=context)
        for line in self.browse(cr, uid, ids, context=context):
            inv_obj.write(cr, uid, [line.invoice_id.id], {'name':line.invoice_id.name },context=context)
        
