# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    OPTIONS = [
        ('void', 'Voids budget move'),
        ('budget', 'Budget move'),
    ]

    budget_move_id = fields.Many2one('cash.budget.move', 'Budget move')
    budget_type = fields.Selection(OPTIONS, 'budget_type', readonly=True)

    @api.one
    def copy(self, default):
        default = {} if default is None else default.copy()
        default.update({
            'budget_move_id': False
        })
        return super(AccountMove, self).copy(default)

    @api.one
    def check_moves_budget(self):
        for move_line in self.line_id:
            if move_line.budget_program_line:
                return True
        return False

    @api.one
    def create_budget_moves(self):
        bud_mov_obj = self.env['cash.budget.move']
        bud_line_obj = self.env['cash.budget.move.line']
        created_move_ids = []
        res_check_moves_budget = self.check_moves_budget()[0]
        if res_check_moves_budget:
            bud_move_id = bud_mov_obj.create(
                {'type': 'manual', 'origin': self.name})
            self.write(
                {'budget_type': 'budget',
                 'budget_move_id': bud_move_id.id})
            created_move_ids.append(bud_move_id)
            for move_line in self.line_id:
                if move_line.budget_program_line:
                    amount = 0.0
                    if move_line.credit > 0.0:
                        amount = move_line.credit * -1
                    if move_line.debit > 0.0:
                        amount = move_line.debit
                    _new_line_id = bud_line_obj.create(
                        {
                            'budget_move_id': bud_move_id.id,
                            'origin': move_line.name,
                            'program_line_id':
                                move_line.budget_program_line.id,
                            'fixed_amount': amount,
                            'move_line_id': move_line.id,
                        })
            bud_move_id.signal_workflow('button_execute')
            bud_move_id.recalculate_values()
        return created_move_ids

    @api.multi
    def rewrite_bud_move_names(self):
        for account_move in self:
            if account_move.budget_move_id:
                account_move.budget_move_id.write(
                    {'origin': account_move.name})

    @api.one
    def post(self):
        res = super(AccountMove, self).post()
        obj_move_line = self.env['account.move.line']
        # Check if this account.move has distributions lines and check
        # (only in valid_moves -> is a account.move object)
        move_lines = self.line_id
        moves_budget = False
        for line in move_lines:
            if line.account_id.moves_cash and\
                    not line.check_distribution_amount():
                raise Warning(_(
                    "The distribution amount for one of this move lines does"
                    "not match with original amount line"
                ))
            if line.budget_program_line:
                moves_budget = True
        if not self.budget_move_id and moves_budget:
            self.create_budget_moves()
        if self.budget_move_id and self.budget_move_id.type in ['manual']:
            self.rewrite_bud_move_names()
        return res

    @api.multi
    def button_cancel(self):
        for acc_move in self:
            bud_move = acc_move.budget_move_id
            if bud_move:
                bud_move.signal_workflow('button_cancel')
                bud_move.signal_workflow('button_draft')
                bud_move.unlink()
        super(AccountMove, self).button_cancel()
        return True

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        for line in res.line_id:
            if line.budget_move_lines:
                res.budget_move_id = line.budget_move_lines[0].budget_move_id
                break
        return res
