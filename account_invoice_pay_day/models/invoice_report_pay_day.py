# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class InvoicePayDay(models.Model):
    _inherit = "account.invoice.report"

    pay_day_related = fields.Selection([('n', 'None'),
                                        ('m', 'Monday'),
                                        ('t', 'Tuesday'),
                                        ('w', 'Wednesday'),
                                        ('r', 'Thursday'),
                                        ('f', 'Friday'),
                                        ('s', 'Saturday'),
                                        ('u', 'Sunday')],
                                       string='Pay Day')

    def _select(self):
        return super(InvoicePayDay, self)._select() + ', sub.pay_day_related'

    def _sub_select(self):
        return super(InvoicePayDay, self)._sub_select() \
               + ', ai.pay_day_related'

    def _group_by(self):
        return super(InvoicePayDay, self)._group_by() + ', ai.pay_day_related'
