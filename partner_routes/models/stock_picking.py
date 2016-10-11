# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class StockPicking(models.Model):

    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def onchange_picking_type(
            self, cr, uid, ids, picking_type_id, partner_id, context=None):
        res = super(StockPicking, self).onchange_picking_type(
            cr, uid, ids, picking_type_id, partner_id, context=context)
        partner = self.pool['res.partner'].browse(
            cr, uid, partner_id, context=context)
        res['value']['partner_route_id'] = partner.partner_route_id.id
        return res

    partner_route_id = fields.Many2one('res.partner.route', string='Route')
