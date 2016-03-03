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
import openerp.addons.decimal_precision as dp


class mro_order_parts_line_extra(models.TransientModel):

    _name = 'mro.parts.extra.part.line'

    name = fields.Char('Description', size=64)
    parts_id = fields.Many2one('product.product', 'Parts', required=True)
    parts_qty = fields.Float(
        'Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    parts_uom = fields.Many2one(
        'product.uom', 'Unit of Measure', required=True)
    maintenance_id = fields.Many2one(
        'mro.order', 'Maintenance Order', select=True)

    @api.onchange('parts_id')
    def onchange_parts(self):
        """onchange handler of parts_id."""
        self.parts_uom = self.parts_id.uom_id


class ExtraPart(models.TransientModel):

    _name = 'mro.parts.extra.part'

    parts_extra_lines = fields.Many2many(
        'mro.parts.extra.part.line',
        relation='mro_parts_ep_ep_line_rel',
        string='Extra Parts')
    maintenance_id = fields.Many2one(
        'mro.order', string='Maintenance Order', select=True)

    @api.multi
    def add_extra_parts(self):
        proc_ids = []
        procurement_obj = self.env['procurement.order']
        part_line_obj = self.env['mro.order.parts.line']
        active_ids = self._context.get('active_ids', [])
        mro_order = self.env['mro.order'].search([('id', '=', active_ids[0])])
        for line in self.parts_extra_lines:
                vals = {
                    'name': mro_order.name + _(' - Extra'),
                    'origin': mro_order.name + _(' - Extra'),
                    'company_id': mro_order.company_id.id,
                    'group_id': mro_order.procurement_group_id.id,
                    'date_planned': mro_order.date_planned,
                    'product_id': line.parts_id.id,
                    'product_qty': line.parts_qty,
                    'product_uom': line.parts_uom.id,
                    'location_id': mro_order.asset_id.property_stock_asset.id
                    }
                proc_id = procurement_obj.create(vals)
                proc_ids.append(proc_id.id)
                vals_line = {
                    'parts_id': line.parts_id.id,
                    'parts_qty': line.parts_qty,
                    'parts_uom': line.parts_uom.id,
                    'maintenance_id': line.maintenance_id.id
                    }
                part_line_obj.create(vals_line)
        procurement_obj.browse(proc_ids).run()
        return True
