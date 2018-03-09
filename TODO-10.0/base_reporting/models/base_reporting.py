# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class Company(models.Model):

    _inherit = 'res.company'

    logo_report = fields.Binary(
        'Report Logo', help='Upload a high definition logo to print '
        'on reports.')
