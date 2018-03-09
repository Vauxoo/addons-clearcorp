# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp.tools.translate import _


class IrModuleModule(models.Model):

    _inherit = 'ir.module.module'

    _sql_constraints = [
         ('force_no_demo_data',
          'CHECK (demo = false)',
          'You cannot install demo data.'),
    ]
