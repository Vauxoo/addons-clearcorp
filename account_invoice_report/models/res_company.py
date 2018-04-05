# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    invoie_rml_footer = fields.Text(string='Invoice Footer')

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'
    
    invoie_rml_footer = fields.Text(related="company_id.logo_report", string='Invoice Footer')
