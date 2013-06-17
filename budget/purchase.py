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

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('published', 'Bill published'),
        ('review', 'Bid review'),
        ('deserted', 'Deserted'),
        ('awarded', 'Awarded'),
        ('ineffectual', 'Ineffectual'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('final_approval', 'Final Approval'),
        ('done', 'Done'),
        ('void', 'Anulled'),
        ('cancel', 'Cancelled')
    ]
    
    _columns = {
        'plan_id' : fields.many2one('budget.plan', 'Budget'),
        'program_id' : fields.many2one('budget.program', 'Program'),
        'program_line_id': fields.many2one('budget.program.line', 'Program line', required=True),
        'reserved_ammount' : fields.float('Reserved', digits=(12,3), readonly=True, required=True, states={'draft':[('readonly',False)]}),
        'budget_move_id': fields.many2one('budget.move', 'Budget move'),
        'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, help="The status of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' status. Then the order has to be confirmed by the user, the status switch to 'Confirmed'. Then the supplier must confirm the order to change the status to 'Approved'. When the purchase order is paid and received, the status becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the status becomes in exception.", select=True),
    }
    
    def onchange_plan(self, cr, uid, ids,plan_id, context=None):
        return {'domain': {'program_id': [('plan_id','=',plan_id),], }}
    
    def onchange_program(self, cr, uid, ids,program_id, context=None):
        return {'domain': {'program_line_id': [('program_id','=',program_id),], }}
    
    def create(self, cr, uid, vals, context=None):
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        obj_order = self.browse(cr,uid,[order],context=context)[0]
        
        bud_move_obj = self.pool.get('budget.move')
        move_id = bud_move_obj.create(cr, uid, {'origin':obj_order.name, 'program_line_id': vals['program_line_id'],'arch_reserved': vals['reserved_ammount']}, context=context)
        self.write(cr, uid,[order],{'budget_move_id':move_id})
        return order
    
    def action_invoice_create(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        acc_inv_mov = self.pool.get('account.invoice')
        res = False
        for id in ids:
            invoice_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)
            acc_inv_mov.write(cr, uid, [invoice_id],{'from_order': True})
            for purchase in self.browse(cr, uid, [id],context=context):
                move = obj_bud_mov.browse(cr,uid,[purchase.budget_move_id])[0]
                move_id = purchase.budget_move_id.id
                obj_bud_mov.write(cr,uid, [purchase.budget_move_id.id],{'account_invoice_ids': [(4, invoice_id)]}, context=context)
                obj_bud_mov.action_execute(cr,uid, [purchase.budget_move_id.id],context=context)
                res = invoice_id
        return res     
    
    def action_publish(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        for purchase in self.browse(cr, uid, ids, context=context):
            move_id = purchase.budget_move_id.id
            obj_bud_mov.action_reserve(cr,uid, [move_id],context=context)
        self.write(cr, uid, ids, {'state': 'published'})
        return True
    
    def action_review(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'review'})
        return True
    
    def action_award(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        for purchase in self.browse(cr, uid, ids, context=context):
            if not purchase.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            move_id = purchase.budget_move_id.id
            obj_bud_mov.action_compromise(cr,uid, [move_id],context=context)
        self.write(cr, uid, ids, {'state': 'awarded'})
        return True
    
    def action_desert(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        for purchase in self.browse(cr, uid, ids, context=context):
            move_id = purchase.budget_move_id.id
            bud_move.action_draft(cr,uid, [move_id],context=context)
        self.write(cr, uid, ids, {'state': 'deserted'})
        return True
    
    def action_ineffectual(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        for purchase in self.browse(cr, uid, ids, context=context):
            move_id = purchase.budget_move_id.id
            obj_bud_mov.action_draft(cr,uid, [move_id],context=context)
        self.write(cr, uid, ids, {'state': 'ineffectual'})
        return True
    
    def action_final_approval(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'final_approval'})
        return True
    
    def action_void(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'void'})
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        for purchase in self.browse(cr, uid, ids, context=context):
            bud_move = purchase.budget_move_id
            obj_bud_mov.action_cancel(cr,uid, [move_id],context=context)
        super(purchase_order, self).action_cancel(cr, uid, ids, context=context)
    
    def action_draft(self, cr, uid, ids, context=None):
        obj_bud_mov = self.pool.get('budget.move')
        for purchase in self.browse(cr, uid, ids, context=context):
            bud_move = purchase.budget_move_id
            if bud_move:
                move_id = purchase.budget_move_id.id
                obj_bud_mov.action_draft(cr,uid, [move_id],context=context)
        self.write(cr, uid, ids, {'state': 'draft'})
    
    
    
    
    