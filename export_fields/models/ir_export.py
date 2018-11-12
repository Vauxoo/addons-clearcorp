# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ExportsFields(models.Model):

    _inherit = 'ir.exports.line'
    sequence = fields.Integer('Sequence', default=1)
    _order = "sequence, id"
