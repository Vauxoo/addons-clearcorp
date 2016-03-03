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

from openerp import models, fields, api, _


class mro_order(models.Model):

    _inherit = 'mro.order'

    def _compute_returned_parts(self):
        for order in self:
            done_line_ids = []
            if order.procurement_group_id:
                for procurement in order.procurement_group_id.procurement_ids:
                    done_line_ids += [
                        move.id for move in procurement.move_ids
                        if move.location_id.id ==
                        order.asset_id.property_stock_asset.id and
                        move.state == 'done'
                    ]
            order.parts_returned_lines = done_line_ids
        return True

    stock_picking_count = fields.Integer(
        'Picking Count', compute='_compute_stock_picking_count')
    parts_returned_lines = fields.Many2many(
        'stock.move', compute='_compute_returned_parts')

    def _compute_stock_picking_count(self):
        if self.procurement_group_id:
            self.stock_picking_count = self.env['stock.picking'].search_count(
                [('group_id', '=', self.procurement_group_id.id)])
        else:
            self.stock_picking_count = 0
        return True

    @api.multi
    def view_related_pickings(self):
        if self.procurement_group_id:
            pickings = self.env['stock.picking'].search(
                [('group_id', '=', self.procurement_group_id.id)])
            domain = [('id', 'in', pickings._ids)]
        else:
            domain = [('id', 'in', [])]
        return {
            'name': _('Pickings'),
            'domain': domain,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }
