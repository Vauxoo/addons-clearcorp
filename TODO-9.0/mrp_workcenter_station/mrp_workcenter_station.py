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
from openerp.exceptions import Warning

class Station(models.Model):
    "Work Center Station"

    _name = 'mrp.workcenter.station.station'
    _description = __doc__
    _order = 'code asc'

    @api.one
    @api.depends('workorder_ids.state')
    def _compute_workorder_items(self):
        self.active_order_id = self.env['mrp.production.workcenter.line']
        self.product_id = self.env['product.product']
        for line in self.workorder_ids:
            if line.state == 'startworking':
                self.active_order_id = line
                self.product_id = line.product
                break

    name = fields.Char('Station Name', size=128, required=True)
    code = fields.Char('Code', size=64, required=True)
    workorder_ids = fields.Many2many('mrp.production.workcenter.line',
        rel='mrp_workorder_station_rel', string='Work Orders')
    active_order_id = fields.Many2one('mrp.production.workcenter.line',
        string='Active Work Order', compute='_compute_workorder_items', store=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', required=True)
    product_id = fields.Many2one('product.product', string='Product',
        compute='_compute_workorder_items', store=True)

    @api.multi
    def name_get(self):
        result = []
        for station in self:
            result.append((station.id, "[%s] - %s" % (station.code or '', station.name or '')))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code must be unique.'),
    ]

class WorkCenterLine(models.Model):

    _inherit = 'mrp.production.workcenter.line'

    @api.onchange('workcenter_id')
    def _onchange_workcenter_id(self):
        self.station_ids = self.env['mrp.workcenter.station.station']

    station_ids = fields.Many2many('mrp.workcenter.station.station',
        rel='mrp_workorder_station_rel', string='Work Center Station', required=True)

    @api.one
    def _check_stations(self):
        recs = self.search([('state','=','startworking'),('id','!=', self.id)])
        for workcenter_line in recs:
            workcenter_station_ids = [x.id for x in workcenter_line.station_ids]
            for station in self.station_ids:
                if station.id in workcenter_station_ids:
                    raise Warning(_('The station %s is being used in another Work '
                                    'Order currently in progress.' % station.display_name))
        return True

    @api.multi
    def action_start_working(self):
        res = super(WorkCenterLine, self).action_start_working()
        self._check_stations()
        return res

    @api.multi
    def action_resume(self):
        res = super(WorkCenterLine, self).action_resume()
        self._check_stations()
        return res