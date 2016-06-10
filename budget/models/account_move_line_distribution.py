# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.translate import _
from openerp import models, fields, api
from openerp.exceptions import Warning


class AccountMoveLineDistribution(models.Model):
    _name = "account.move.line.distribution"
    _inherit = "account.distribution.line"
    _description = "Account move line distribution"

    reconcile_ids = fields.Many2many(
        'account.move.reconcile', 'bud_reconcile_distribution_ids',
        string='Budget Reconcile Distributions')
    account_move_line_type = fields.Selection(
        [('liquid', 'Liquid'), ('void', 'Void')], string='Budget Type',
        select=True)
    target_budget_move_line_id = fields.Many2one(
        'budget.move.line', 'Target Budget Move Line',)
    type = fields.Selection(
        [('manual', 'Manual'), ('auto', 'Automatic')],
        string='Distribution Type', select=True, default='manual')
    distribution_amount = fields.Float(default=0.0)
    distribution_percentage = fields.Float(default=0.0)

    # ======== Check distribution percentage.
    # Use distribution_percentage_sum in account.move.line to check
    @api.one
    @api.constrains('account_move_line_id')
    def _check_distribution_percentage(self):
        # distribution_percentage_sum compute all the percentages for a
        # specific move line.
        line_percentage = 0.0
        if self.account_move_line_id.distribution_percentage_sum:
            line_percentage =\
                self.account_move_line_id.distribution_percentage_sum -\
                self.distribution_percentage
        line_percentage_remaining = 100 - line_percentage
        if self.distribution_percentage >\
                line_percentage_remaining:
            raise Warning(_("""
            The distribution percentage can not be greater than sum of all
            percentage for the account move line selected
            """))

    # ========= Check distribution percentage. Use distribution_amount_sum in
    # account.move.line to check
    @api.one
    @api.constrains('distribution_amount')
    def _check_distribution_amount(self):
        amount = 0.0
        line_amount_dis = 0.0
        # ==== distribution_amount_sum compute all the percentages for a
        # specific move line.
        if self.account_move_line_id.distribution_amount_sum:
            line_amount_dis =\
                self.account_move_line_id.distribution_amount_sum -\
                self.distribution_amount
        # =====Find amount for the move_line
        if self.account_move_line_id.credit > 0:
            amount = self.account_move_line_id.credit
        if self.account_move_line_id.debit > 0:
            amount = self.account_move_line_id.debit
        # Only in case of budget self
        if self.account_move_line_id.credit == 0 and\
                self.account_move_line_id.debit == 0:
            if self.account_move_line_id.fixed_amount:
                amount = self.account_move_line_id.fixed_amount
        # Check which is the remaining between the amount line and sum of
        # amount in selfs.
        amount_remaining = amount - line_amount_dis
        if self.distribution_amount > amount_remaining:
            raise Warning(_("""
                The distribution amount can not be greater than maximum amount
                of remaining amount for account move line selected
            """))

    # Check the plan for distribution line
    @api.multi
    def get_plan_for_distributions(self, dist_ids):
        query = """
        SELECT AMLD.id AS dist_id, BP.id AS plan_id FROM
            account_move_line_distribution AMLD
            INNER JOIN budget_move_line BML ON
                AMLD.target_budget_move_line_id = BML.id
            INNER JOIN  budget_move BM ON BML.budget_move_id=BM.id
            INNER JOIN budget_program_line BPL ON BPL.id=BML.program_line_id
            INNER JOIN budget_program BPR ON BPR.id=BPL.program_id
            INNER JOIN budget_plan BP ON BP.id=BPR.plan_id
            WHERE AMLD.id IN %s"""
        params = (tuple(dist_ids),)
        self._cr.execute(query, params)
        result = self._cr.dictfetchall()
        return result

    @api.one
    @api.constrains('distribution_amount')
    def _check_plan_distribution_line(self):
        plan_obj = self.env['budget.plan']
        # Get plan for distribution lines
        result = self.get_plan_for_distributions(self._ids)
        # Check plan's state
        for dist_id in result:
            plan = plan_obj.browse([dist_id['plan_id']])[0]
            if plan.state in ('closed', 'cancel'):
                raise Warning(_("""
                    You cannot create a distribution with a closed or cancelled
                    plan
                """))

    # A distribution line only has one target. This target can be a move_line
    # or a budget_line
    @api.one
    @api.constrains('target_budget_move_line_id',
                    'target_account_move_line_id')
    def _check_target_move_line(self):
        if self.target_budget_move_line_id and\
                self.target_account_move_line_id:
            raise Warning(_("""
                A Distribution Line only has one target. A target can be a move
                line or a budget move line
            """))

    # Distribution amount must be less than compromised amount in budget move
    # line
    @api.one
    @api.constrains('distribution_amount')
    def _check_distribution_amount_budget(self):
        # computes = self.target_budget_move_line_id.compute(
        #    ignore_dist_ids=[self.id])
        compromised = round(
            self.target_budget_move_line_id.compromised,
            self.env['decimal.precision'].precision_get('Account'))
        
        if abs(self.distribution_amount) > abs(compromised):
            print "\n _check_distribution_amount_budget: ", compromised
            raise Warning(_("""
                The distribution amount can not be greater than compromised
                amount in budget move line selected: self.distri_amount %s , compro: %s
            """ % (self.distribution_amount, compromised)))

    @api.model
    def clean_reconcile_entries(self, move_line_ids):
        for move_line_id in move_line_ids:
            result = self.search([('account_move_line_id', '=', move_line_id)])
            result.unlink()

    @api.multi
    def _account_move_lines_mod(self):
        lines = []
        for line in self:
            lines.append(line.account_move_line_id.id)
        return lines

    @api.model
    def create(self, vals):
        if self.env.context:
            dist_type = self.env.context.get('distribution_type', 'auto')
        else:
            dist_type = 'auto'
        vals['type'] = dist_type
        res = super(AccountMoveLineDistribution, self).create(vals)
        return res

    @api.one
    def write(self, vals):
        plan_obj = self.env['budget.plan']

        # Get plan for distribution lines
        result = self.get_plan_for_distributions(self._ids)

        # Check plan's state
        for dist_id in result:
            plan = plan_obj.browse([dist_id['plan_id']])
            if plan.state in ('closed'):
                raise Warning(
                    _('You cannot modify a distribution with a closed plan'))
        super(AccountMoveLineDistribution, self).write(vals)

    @api.one
    def unlink(self, is_incremental=False):
        plan_obj = self.env['budget.plan']
        bud_move_obj = self.env['budget.move']
        if self:
            result = self.get_plan_for_distributions(self._ids)
            # Check plan's state
            for dist_id in result:
                plan = plan_obj.browse([dist_id['plan_id']])[0]
                if plan.state in ('closed'):
                    if not is_incremental:
                        raise Warning(_(
                            """
                    You cannot delete a distribution with a closed plan"""))
            move_ids = []
            if self.target_budget_move_line_id:
                move_ids.append(
                    self.target_budget_move_line_id.budget_move_id.id)
            super(AccountMoveLineDistribution, self).unlink()
            bud_move_obj.recalculate_values(move_ids)
