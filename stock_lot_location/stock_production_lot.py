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


class ProductionLot(models.Model):

    _inherit = 'stock.production.lot'

    @api.one
    def _get_latest_quant(self, filters=[]):
        domain = list(filters)
        domain.append(('id', 'in', self.quant_ids.ids))
        return self.quant_ids.search(domain, limit=1, order='in_date desc')

    @api.one
    @api.depends('quant_ids')
    def _compute_quant_locations(self):
        self.location_id = self.env['stock.location']
        if len(set(
                map(lambda quant:
                    quant.location_id.id, self.quant_ids))) == 1:
            self.location_id = self.quant_ids[0].location_id

    @api.one
    @api.depends('location_id')
    def _compute_partner(self):
        self.partner_id = self.env['res.partner']
        if self.location_id:
            latest_quant = self._get_latest_quant()
            if latest_quant:
                latest_quant = latest_quant[0]
                latest_move = latest_quant._get_latest_move_with_location(
                    filters=[('location_dest_id', '=', self.location_id.id)])
                if latest_move:
                    latest_move = latest_move[0]
                    self.partner_id = latest_move.partner_id

    location_id = fields.Many2one(
        'stock.location', string='Location',
        compute='_compute_quant_locations', store=True)
    partner_id = fields.Many2one(
        'res.partner', string='Destination Address',
        compute='_compute_partner', store=True)
