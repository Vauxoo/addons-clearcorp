# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _


class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.multi
    def reverse_moves(self, date=None, journal_id=None):
        reverse_moves = super(AccountMove, self).reverse_moves(
            date, journal_id)
        if reverse_moves:
            reverse_move_id = reverse_moves[0]
            for move in self:
                for line in move.line_ids:
                    if line.account_id.reconcile:
                        to_reconcile_lines = self.env['account.move.line']
                        to_reconcile_lines += line
                        if line.reconciled:
                            line.remove_move_reconcile()
                        domain = [
                            ('credit', '=', line.debit),
                            ('debit', '=', line.credit),
                            ('account_id', '=', line.account_id.id),
                            ('amount_currency', '=', -line.amount_currency),
                            ('move_id', '=', reverse_move_id)
                        ]
                        tmpline = self.env['account.move.line'].search(domain)
                        to_reconcile_lines += tmpline
                        to_reconcile_lines.reconcile()
        return reverse_moves
