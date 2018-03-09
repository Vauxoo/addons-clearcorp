# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.onchange('amount_currency', 'currency_id')
    def onchange_amount_currency(self):
        """This method provides conversion of the amount_currency to debit
        or credit depending on the currency selected."""

        if self.amount_currency and self.currency_id:
            company_currency = self.move_id.company_id.currency_id

            ctx = {}
            if self.move_id.date:
                ctx.update({'date': self.move_id.date})

            exchange_amount = self.currency_id.with_context(ctx).compute(
                abs(self.amount_currency), company_currency)

            # 4. Assign values to debit or credit
            if self.amount_currency >= 0:
                self.debit = exchange_amount
                self.credit = 0.0
            else:
                self.credit = exchange_amount
                self.debit = 0.0
