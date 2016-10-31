# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ClientPayDay(models.Model):
    _inherit = 'res.partner'

    pay_day = fields.Selection([('n', 'None'),
                                ('m', 'Monday'),
                                ('t', 'Tuesday'),
                                ('w', 'Wednesday'),
                                ('r', 'Thursday'),
                                ('f', 'Friday'),
                                ('s', 'Saturday'),
                                ('u', 'Sunday')],
                               string='Pay Day', required=True, default='n')
