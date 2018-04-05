# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class Company(models.Model):

    _inherit = 'res.company'

    logo_report = fields.Binary(
        'Report Logo', help='Upload a high definition logo to print '
        'on reports.')

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'
    
    logo_report = fields.Binary(related="company_id.logo_report", string="Report Logo", help="Upload a high definition logo to print on reports.")
