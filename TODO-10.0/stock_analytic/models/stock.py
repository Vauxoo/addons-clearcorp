# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class stock_move(models.Model):
    _inherit = "stock.move"

    account_analytic_id = fields.Many2one('account.analytic.account',
                                          'Analytic account')

    def _create_account_move_line(self, cr, uid, move, src_account_id,
                                  dest_account_id, reference_amount,
                                  reference_currency_id, context=None):
        res = super(stock_move,
                    self)._create_account_move_line(cr, uid,
                                                    move,
                                                    src_account_id,
                                                    dest_account_id,
                                                    reference_amount,
                                                    reference_currency_id,
                                                    context=context
                                                    )
        if move.account_analytic_id:
            for _val1, _val2, vals in res:
                vals['analytic_account_id'] = move.account_analytic_id.id
        return res


class stock_quant(models.Model):

    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost,
                                   credit_account_id, debit_account_id,
                                   context=None):
        res = super(stock_quant,
                    self)._prepare_account_move_line(cr,
                                                     uid, move, qty, cost,
                                                     credit_account_id,
                                                     debit_account_id,
                                                     context=context
                                                     )
        if res and res[0] and res[0][2]:
            # Add analytic account in debit line
            res[0][2].update({
                 'analytic_account_id': move.account_analytic_id.id,
            })
        return res
