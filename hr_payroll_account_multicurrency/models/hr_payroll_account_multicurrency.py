# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def process_sheet(self):
        for payslip in self:
            super(HRPayslip, self).process_sheet()
            if payslip.currency_id:
                account_move = self.env['account.move'].search(
                    [('ref', '=', payslip.number)])
                for account_move_line in account_move.line_id:
                    currency_id = self.company_id.currency_id
                    if account_move_line.credit > 0.0:
                        account_move_line.write({
                            'amount_currency': -1 * account_move_line.credit,
                            'currency_id': payslip.currency_id.id
                        })
                        account_move_line.credit = self.currency_id.with_context(
                            {'date': account_move.date}
                        ).compute(account_move_line.credit, currency_id)
                    if account_move_line.debit > 0.0:
                        account_move_line.write({
                            'amount_currency': account_move_line.debit,
                            'currency_id': payslip.currency_id.id
                        })
                        account_move_line.debit = self.currency_id.with_context(
                            {'date': account_move.date}
                        ).compute(account_move_line.debit, currency_id)
