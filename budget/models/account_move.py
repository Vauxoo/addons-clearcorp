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

    budget_move_id = fields.Many2one('budget.move', 'Budget move')
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
        bud_mov_obj = self.env['budget.move']
        bud_line_obj = self.env['budget.move.line']
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
        context = self.env.context
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate()

        if not valid_moves:
            raise ValidationError(_(
                """You cannot validate a non-balanced entry.
                Make sure you have configured payment terms properly.
                The latest payment term line should be of the "Balance" type.
                """))
        _created_move_ids = self.create_budget_moves()
        # ===========================================================
        check_lines = []
        next_step = False
        amount = 0.0
        percentage = 0.0
        obj_move_line = self.env['account.move.line']

        # Check if this account.move has distributions lines and check
        # (only in valid_moves -> is a account.move object)
        for move in self.browse(valid_moves):
            move_lines = obj_move_line.search([('move_id', '=', move.id)])
            for line in move_lines:
                if line.account_id.moves_cash:
                    check_lines.append(line)
            # Check amount in line.distribution (if there exist any line.id)
            if len(check_lines) > 0:
                for line in check_lines:
                    distribution_lines =\
                        self.env['account.move.line.distribution'].search(
                            [('account_move_line_id', '=', line.id)])
                    if len(distribution_lines) > 0:
                        # Sum distribution_amount. This amount is equal to
                        # line.amount (debit or credit).
                        for distribution in distribution_lines:
                            amount += distribution.distribution_amount
                            percentage += distribution.distribution_percentage
                        # Find amount (debit or credit) and compare.
                        if line.debit > 0:
                            amount_check = line.debit
                        else:
                            amount_check = line.credit
                        # Continue with normal process
                        if (amount_check == amount) and (percentage == 100):
                            next_step = True
                        else:
                            next_step = False
                            return {
                                'value': {'account_move_line_id': line.id},
                                'warning': {
                                    'title': 'Warning',
                                    'message': """
                                    Distribution amount for this move line does
                                    not match with original amount line"""
                                }
                            }
                    # Continue with normal process
                    else:
                        next_step = True
            else:
                next_step = True
            # ===============================================================#
            if next_step:
                for move in self.browse(valid_moves):
                    if move.name == '/':
                        new_name = False
                        journal = move.journal_id
                        if invoice and invoice.internal_number:
                            new_name = invoice.internal_number
                        else:
                            if journal.sequence_id:
                                new_name = journal.sequence_id.next_by_id(
                                    move.period_id.fiscalyear_id.id)
                            else:
                                raise ValidationError(_(
                                    'Please define a sequence on the journal.'
                                    ))
                        if new_name:
                            move.write({'name': new_name})
                update_query =\
                    "UPDATE account_move SET state=%s WHERE id IN %s"
                self._cr.execute(update_query, ('posted', tuple(valid_moves)))
        super_result = super(AccountMove, self).post()
        self.rewrite_bud_move_names()
        return super_result

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
