# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp



class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        obj_bud_mov = self.pool.get('budget.move')
        obj_bud_line = self.pool.get('budget.move.line')
        purchase_line_obj = self.pool.get('purchase.order.line')
        invoice_obj = self.pool.get('account.invoice')
        purchase_obj = self.pool.get('purchase.order')
        invoice_line_obj = self.pool.get('account.invoice.line')
        
        invoices= super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id=journal_id, group=group, type=type, context=context)
        res = {}
        res= {'res':invoices,}
        
        for picking in res.keys():
            invoice_id = res[picking]
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
            for invoice_line in invoice.invoice_line:
            #purchase_order_line_invoice_rel
                cr.execute('''SELECT order_line_id FROM purchase_order_line_invoice_rel \
                WHERE invoice_id = %s''',(invoice_line.id,))
                count = cr.fetchall()
                for po_line_id in count:
                    po_line = purchase_line_obj.browse(cr, uid, [po_line_id[0]], context=context)
                    asoc_bud_line_id = obj_bud_line.search(cr, uid, [('po_line_id','=',po_line.id), ])[0]
                    obj_bud_line.write(cr, uid, [asoc_bud_line_id],{'inv_line_id': invoice_line.id}, context=context)
                    move_id = po_line.order_id.budget_move_id.id
                    invoice_obj.write(cr, uid, invoice_id, {'budget_move_id': move_id, 'from_order':True}, context=context)
                    obj_bud_mov.signal_workflow(cr, uid, [move_id], 'button_execute', context=context)
        return invoices
            
            