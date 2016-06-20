# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MrpBomLineHistory(models.Model):

    _inherit = 'mrp.bom.line'
    _name = 'mrp.bom.line.history'
    _description = 'Bill of Material Line History'

    bom_id = fields.Many2one('mrp.bom.history')
