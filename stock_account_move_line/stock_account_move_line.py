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

    def compute_unit_cost(self,cr, uid, quantity, debit, credit, context={}):
        cost = 0.0
        if quantity != 0.0:
            cost = (debit + credit) / quantity
        return cost

    def compute_unit_cost_currency(self, cr, uid, stock_picking, unit_cost, context = {}):
        currency = False
        if stock_picking.sale_id:
            currency = stock_picking.sale_id.currency_id or False
        else:
            for move in stock_picking.move_lines:
                if move.purchase_line_id.order_id:
                    currency = move.purchase_line_id.order_id.currency_id or False
                    break
        if not currency or currency == stock_picking.company_id.currency_id:
            unit_cost_currency = 0.0
        else:
            company_currency = stock_picking.company_id.currency_id
            unit_cost_currency = self.pool.get('res.currency').compute(cr, uid,
                                            company_currency.id, currency.id, unit_cost,
                                            context=context)
        return unit_cost_currency

    unit_cost = fields.Float('Unit Cost')
    unit_cost_currency = fields.Float('Unit Cost Currency')
    stock_move_id = fields.Many2one('stock.move', string='Stock Move')
    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')


class stock_quant(models.Model):

    _inherit = "stock.quant"

    def _prepare_account_move_line(self, cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=None):
        res = super(stock_quant, self)._prepare_account_move_line(cr, uid, move, qty, cost, credit_account_id, debit_account_id, context=context)
        debit_line_vals = res[0][2]
        credit_line_vals = res[1][2]
        move_line_obj = self.pool.get('account.move.line')
        unit_cost_debit = move_line_obj.compute_unit_cost(cr, uid, quantity = debit_line_vals['quantity'],
                                                                            debit = debit_line_vals['debit'],
                                                                            credit = debit_line_vals['credit'],
                                                                            context = context)
        unit_cost_credit = move_line_obj.compute_unit_cost(cr, uid, quantity = credit_line_vals['quantity'],
                                                                            debit = credit_line_vals['debit'],
                                                                            credit = credit_line_vals['credit'],
                                                                            context = context)
        debit_line_vals.update({'stock_move_id': move.id,
                                'stock_picking_id': move.picking_id.id,
                                'unit_cost': unit_cost_debit,
                                'unit_cost_currency': move_line_obj.compute_unit_cost_currency(cr, uid, move.picking_id, unit_cost_debit, context=context),

                                })
        credit_line_vals.update({'stock_move_id': move.id,
                                 'stock_picking_id': move.picking_id.id,
                                 'unit_cost': unit_cost_credit,
                                 'unit_cost_currency': move_line_obj.compute_unit_cost_currency(cr, uid, move.picking_id, unit_cost_credit, context=context),
                                 })
        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        return res
