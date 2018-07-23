# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class Structure(models.Model):

    _inherit = 'hr.payroll.structure'

    active = fields.Boolean(default=True)
