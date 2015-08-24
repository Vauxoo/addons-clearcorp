# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import models, fields, api


class account_move_line(models.Model):

    _inherit = "account.move.line"

    @api.one
    def _compute_unit_cost(self):
        cost = 0.0
        if self.quantity != 0.0:
            cost = self.debit + self.credit / self.quantity
            self.unit_cost = cost
    @api.one
    def _compute_unit_cost_currency(self):
        currency = False
        if self.stock_picking_id.sale_id:
            currency = self.stock_picking_id.sale_id.currency_id or False
        else:
            for move in self.stock_picking_id.move_lines:
                if move.purchase_line_id.order_id:
                    currency = move.purchase_line_id.order_id.currency_id or False
                    break
        if not currency or currency == self.company_id.currency_id:
            self.unit_cost_currency = 0.0
        else:
            self.unit_cost_currency = currency.compute(self.unit_cost,
                                                       self.company_id.currency_id)

    unit_cost = fields.Float('Unit Cost', compute='_compute_unit_cost', store=True)
    unit_cost_currency = fields.Float('Unit Cost Currency',
                                      compute='_compute_unit_cost_currency', store=True)
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')


class stock_quant(models.Model):

    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        res = super(stock_quant, self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]
        debit_line_vals.update({'stock_move_id': move.id,
                                'stock_picking_id': move.picking_id.id,
                                })
        credit_line_vals.update({'stock_move_id': move.id,
                                 'stock_picking_id': move.picking_id.id,
                                 })
        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
