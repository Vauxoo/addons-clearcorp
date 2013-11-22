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



class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        obj_bud_mov = self.pool.get('budget.move')
        obj_bud_line = self.pool.get('budget.move.line')
        purchase_line_obj = self.pool.get('purchase.order.line')
        invoice_obj = self.pool.get('account.invoice')
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        invoice_line_obj = self.pool.get('account.invoice.line')
        
        res= super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id=journal_id, group=group, type=type, context=context)
        
        for picking in res.keys():
            invoice_id = res[picking]
            invoice = invoice_obj.browse(cr, uid, [invoice_id], context=context)
            for invoice_line in invoice.invoice_line:
            #purchase_order_line_invoice_rel
                
                po_line_id = purchase_line_obj.search(cr, uid,[(invoice_line.id,'in','invoice_lines')],context=context)[0] 
        
                po_line = purchase_line_obj.browse(cr, uid, [po_line_id], context=context)
                asoc_bud_line_id = obj_bud_line.search(cr, uid, [('po_line_id','=',po_line.id), ])[0]
                obj_bud_line.write(cr, uid, [asoc_bud_line_id],{'inv_line_id': invoice_line.id}, context=context)
                move_id = po_line.order_id.budget_move_id.id
                invoice_obj.write(cr, uid, [invoice_id], {'budget_move_id': move_id, 'from_order':True}, context=context)
                obj_bud_mov._workflow_signal(cr, uid, [move_id], 'button_execute', context=context)
        return result
            
            