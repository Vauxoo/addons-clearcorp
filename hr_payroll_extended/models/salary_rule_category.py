# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class SalaryRuleCategory(models.Model):

    _inherit = 'hr.salary.rule.category'

    active = fields.Boolean(default=True)
