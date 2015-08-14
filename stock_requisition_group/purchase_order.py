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

from openerp import models, api


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def _prepare_order_line_move(
            self, order, order_line, picking_id, group_id):
        if order.requisition_id and order.requisition_id.group_id:
            if group_id:
                group = self.env['procurement.group'].browse(group_id)
                group.unlink()
            group_id = order.requisition_id.group_id.id
        return super(PurchaseOrder, self)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
