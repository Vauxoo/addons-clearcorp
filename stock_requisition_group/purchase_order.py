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

from openerp import models, fields, api
from openerp.api import onchange


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(
            self, order, order_line, picking_id, group_id):
        if order.requisition_id:
            if order.requisition_id.group_id:
                if group_id:
                    group = self.env['procurement.group'].browse(group_id)
                    group.unlink()
                group_id = order.requisition_id.group_id.id
        move_lines = super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        if order_line.procurement_ids and \
                order_line.procurement_ids.move_dest_id:
            for i in range(0, len(move_lines)):
                dest_id = order_line.procurement_ids.move_dest_id
                move_lines[i]['move_dest_id'] = dest_id.id
        return move_lines

    @api.multi
    def wkf_confirm_order(self):
        for po in self:
            for line in po.order_line:
                line.match_procurement()
        return True


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.one
    def match_procurement(self):
        if self.requisition_id and not self.procurement_ids:
            # rq_line_obj = self.env['purchase.requisition.line']
            self._cr.execute("""SELECT prl.id, prl.product_qty,
(SELECT COUNT(*)
 FROM procurement_order
 WHERE purchase_line_id = prl.id) AS assigned
FROM purchase_requisition_line AS prl
WHERE prl.requisition_id = %s
AND prl.product_id = %s""", [self.requisition_id.id,
                             self.product_id.id])
            possible_matches = self._cr.dictfetchall()
            # Find the perfect match
            for match in possible_matches:
                if match['product_qty'] - \
                        match['assigned'] == self.product_qty:
                    self.procurement_ids = [(4, match['id'])]
                    return True
            # Fit it in place with a posible match
            for match in possible_matches:
                if match['product_qty'] - \
                        match['assigned'] < self.product_qty:
                    return True
            # Raise an error if no match is found
            raise Exception

    requisition_id = fields.Many2one(
        'purchase.requisition', related='order_id.requisition_id',
        string='Requisition', readonly=True)
