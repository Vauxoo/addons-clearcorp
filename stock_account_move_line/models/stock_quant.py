# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _prepare_account_move_line(
            self, cr, uid, move, qty, cost, credit_account_id,
            debit_account_id, context=None):

        res = super(StockQuant, self)._prepare_account_move_line(
            cr, uid, move, qty, cost, credit_account_id, debit_account_id,
            context=context)

        move_line_obj = self.pool.get('account.move.line')

        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]

        unit_cost_debit = move_line_obj._compute_unit_cost(
            cr, uid, move.id, quantity=debit_line_vals['quantity'],
            debit=debit_line_vals['debit'], credit=debit_line_vals['credit'],
            context=context)
        unit_cost_credit = move_line_obj._compute_unit_cost(
            cr, uid, move.id, quantity=credit_line_vals['quantity'],
            debit=credit_line_vals['debit'], credit=credit_line_vals['credit'],
            context=context)

        debit_line_vals.update({
            'stock_move_id': move.id,
            'stock_picking_id': move.picking_id.id,
            'unit_cost': unit_cost_debit,
            'unit_cost_currency': move_line_obj._compute_unit_cost_currency(
                cr, uid, move.id, move.picking_id, unit_cost_debit,
                context=context)
        })
        credit_line_vals.update({
            'stock_move_id': move.id,
            'stock_picking_id': move.picking_id.id,
            'unit_cost': unit_cost_credit,
            'unit_cost_currency': move_line_obj._compute_unit_cost_currency(
                cr, uid, move.id, move.picking_id, unit_cost_credit,
                context=context)
        })

        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
