# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PartnerRoute(models.Model):

    _name = 'res.partner.route'
    _description = 'Partner Route'

    name = fields.Char('Name', required=True)


class Partner(models.Model):

    _inherit = 'res.partner'
    _name = 'res.partner'

    partner_route_id = fields.Many2one('res.partner.route', string='Route')
