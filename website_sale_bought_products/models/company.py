# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class Company(models.Model):

    _inherit = 'res.company'

    bought_product_limit = \
        fields.Float('Suggested Products Display',
                     digits_compute=0,
                     default=5,
                     help='Max suggested products to be display.')
