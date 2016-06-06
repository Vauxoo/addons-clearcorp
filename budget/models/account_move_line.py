# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # ========================================================================
    #
    # distribution_percentage_sum compute the percentage for the
    # account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    #
    # distribution_amount_sum compute the amount for the account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    #
    # account_move_lines_mod method return the account.move.line id's where the
    # store apply the change. This method is necessary to create a store. This
    # help to compute in a "automatic way" those fields (percentage and sum)
    # and is easier to get this values from those fields.
    #
    # =========================================================================

    @api.one
    @api.depends('account_move_line_dist')
    def _sum_distribution_per(self):
        if self.account_move_line_dist:
            query = """
                SELECT amld.id, SUM(amld.distribution_percentage) AS dis_per
                    FROM account_move_line_distribution amld
                    WHERE amld.id IN %s GROUP BY amld.id"""
            params = [(self.account_move_line_dist.id,)]
            self._cr.execute(query, params)
            for row in self._cr.dictfetchall():
                self.distribution_percentage_sum = row['dis_per']

    @api.one
    @api.depends('account_move_line_dist')
    def _sum_distribution_amount(self):
        if self.account_move_line_dist:
            query = """
                SELECT amld.id, SUM(amld.distribution_amount) AS dis_amount
                    FROM account_move_line_distribution amld
                    WHERE amld.id=%s GROUP BY amld.id"""
            params = [self.account_move_line_dist.id]
            self._cr.execute(query, params)
            for row in self._cr.dictfetchall():
                self.distribution_amount_sum = abs(row['dis_amount'])

    @api.multi
    def _account_move_lines_mod(self, amld_ids):
        list_amld = []
        amld_obj = self.env['account.move.line.distribution']
        for line in amld_obj.browse(amld_ids):
            list_amld.append(line.account_move_line_id.id)
        return list_amld

    @api.multi
    def name_get(self):
        result = []
        for line in self:
            deb = ""
            cred = ""
            am_curr = ""
            if line.debit:
                deb = _("D:") + str(round(
                    line.debit,
                    self.env['decimal.precision'].precision_get('Account')))
            if line.credit:
                cred = _("C:") + str(round(
                    line.credit,
                    self.env['decimal.precision'].precision_get('Account')))
            if line.amount_currency:
                am_curr = _("AC:") + str(round(
                    line.amount_currency,
                    self.env['decimal.precision'].precision_get('Account')))
            if line.ref:
                result.append((
                    line.id,
                    (line.move_id.name or '') + ' (' + line.ref + ')' + " " +
                    deb + " " + cred + " " + am_curr))
            else:
                result.append((
                    line.id,
                    line.move_id.name + " " + deb + " " + cred + " " + am_curr
                    ))
        return result

    @api.one
    def copy(self, default=None):
        default = {} if default is None else default.copy()
        default.update({
            'budget_move_lines': False
        })
        return super(AccountMoveLine, self).copy(default)

    @api.one
    def copy_data(self, default=None):
        default = {} if default is None else default.copy()
        default.update({
            'budget_move_lines': False
        })
        return super(AccountMoveLine, self).copy_data(default)

    # =======Budget Move Line
    budget_move_lines = fields.One2many(
        'budget.move.line', 'move_line_id', 'Budget Move Lines')

    # =======Percentage y amount distribution
    distribution_percentage_sum = fields.Float(
        compute='_sum_distribution_per', string="Distributed percentage",
        default=0.0,
        store=True)
    distribution_amount_sum = fields.Float(
        compute='_sum_distribution_amount', string="Distributed amount",
        default=0.0,
        store=True)

    # =======account move line distributions
    account_move_line_dist = fields.One2many(
        'account.move.line.distribution', 'account_move_line_id',
        string='Account Move Line Distributions')
    type_distribution = fields.Selection(
        related='account_move_line_dist.type', string="Distribution type")

    # ======budget program line
    budget_program_line = fields.Many2one(
        'budget.program.line', 'Budget Program Line')
