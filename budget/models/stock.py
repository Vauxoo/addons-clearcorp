# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def action_invoice_create(self, journal_id=False, group=False,
                              type='out_invoice'):
        obj_bud_mov = self.env['budget.move']
        obj_bud_line = self.env['budget.move.line']
        purchase_line_obj = self.env['purchase.order.line']
        invoice_obj = self.env['account.invoice']
        invoices = super(StockPicking, self).action_invoice_create(
            journal_id=journal_id, group=group, type=type)
        res = {'res': invoices}
        for picking in res.keys():
            invoice_id = res[picking]
            invoice = invoice_obj.browse(invoice_id)
            for invoice_line in invoice.invoice_line:
                # purchase_order_line_invoice_rel
                self._cr.execute('''SELECT order_line_id FROM purchase_order_line_invoice_rel \
                WHERE invoice_id = %s''' % invoice_line.id)
                count = self._cr.fetchall()
                for po_line_id in count:
                    po_line = purchase_line_obj.browse([po_line_id[0]])
                    asoc_bud_line_id = obj_bud_line.search([
                        ('po_line_id', '=', po_line.id)])[0]
                    obj_bud_line.write([asoc_bud_line_id],
                                       {'inv_line_id': invoice_line.id}, )
                    move_id = po_line.order_id.budget_move_id.id
                    invoice_obj.write(invoice_id, {'budget_move_id': move_id,
                                                   'from_order': True})
                    obj_bud_mov.signal_workflow([move_id], 'button_execute')
        return invoices
