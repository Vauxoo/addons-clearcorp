# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):

        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
        if not res:
            return res

        move_line_obj = self.env['account.move.line']

        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]

        unit_cost_debit = move_line_obj._compute_unit_cost(
            quantity=debit_line_vals['quantity'],
            debit=debit_line_vals['debit'],
            credit=debit_line_vals['credit'])
        unit_cost_credit = move_line_obj._compute_unit_cost(
            quantity=credit_line_vals['quantity'],
            debit=credit_line_vals['debit'],
            credit=credit_line_vals['credit'])

        debit_line_vals.update({
            'stock_move_id': self.id,
            'stock_picking_id': self.picking_id.id,
            'unit_cost': unit_cost_debit,
            'unit_cost_currency': move_line_obj._compute_unit_cost_currency(self.picking_id, unit_cost_debit)
        })
        credit_line_vals.update({
            'stock_move_id': self.id,
            'stock_picking_id': self.picking_id.id,
            'unit_cost': unit_cost_credit,
            'unit_cost_currency': move_line_obj._compute_unit_cost_currency(self.picking_id, unit_cost_credit)
        })

        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
