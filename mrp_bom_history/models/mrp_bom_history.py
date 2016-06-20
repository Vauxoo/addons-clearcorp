# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class MrpBomHistory(models.Model):

    _inherit = 'mrp.bom'
    _name = 'mrp.bom.history'
    _order = 'create_date DESC'
    _description = 'Bill of Material History'

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material', required=True, ondelete='cascade')
    bom_line_ids = fields.One2many('mrp.bom.line.history', copy=False)
