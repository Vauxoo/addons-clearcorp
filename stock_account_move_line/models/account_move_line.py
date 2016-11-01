# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.multi
    def _compute_unit_cost(self, quantity, debit, credit):
        assert self.ensure_one()
        cost = 0.0
        if quantity != 0.0:
            cost = (debit + credit) / quantity
        return cost

    @api.multi
    def _compute_unit_cost_currency(self, stock_picking, unit_cost):
        assert self.ensure_one()
        currency = False
        if stock_picking.sale_id:
            currency = stock_picking.sale_id.currency_id or False
        else:
            for move in stock_picking.move_lines:
                if move.purchase_line_id.order_id:
                    currency = move.purchase_line_id.order_id.currency_id \
                        or False
                    break
        if not currency or currency == stock_picking.company_id.currency_id:
            unit_cost_currency = 0.0
        else:
            company_currency = stock_picking.company_id.currency_id
            unit_cost_currency = company_currency.compute(
                currency.id, unit_cost)
        return unit_cost_currency

    unit_cost = fields.Float('Unit Cost')
    unit_cost_currency = fields.Float('Unit Cost Currency')
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')
