# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class InvoicePayDay(models.Model):
    _inherit = "account.invoice"

    pay_day_related = fields.Selection([('n', 'None'),
                                        ('m', 'Monday'),
                                        ('t', 'Tuesday'),
                                        ('w', 'Wednesday'),
                                        ('r', 'Thursday'),
                                        ('f', 'Friday'),
                                        ('s', 'Saturday'),
                                        ('u', 'Sunday')],
                                       string='Pay Day',
                                       readonly=True, store=True,
                                       related='partner_id.pay_day')
