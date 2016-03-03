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

from openerp import models, fields, api, _

class AnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.one
    def _compute_recursive_budget_amount(self):
        budget_amount = 0.0
        for line in self.crossovered_budget_line:
            budget_amount += line.planned_amount + line.practical_amount
        return sum([budget_amount] + [child_account._compute_recursive_budget_amount()[0] for
            child_account in self.child_complete_ids])

class Project(models.Model):

    _inherit = 'project.project'

    @api.multi
    def view_crossovered_budget_lines(self):
        analytic_account_obj = self.env['account.analytic.account']
        analytic_accounts = analytic_account_obj.search([
            ('id','child_of',self.analytic_account_id.id)])
        line_ids = []
        for account in analytic_accounts:
            line_ids += account.crossovered_budget_line.ids
        view_id = self.env['ir.model.data'].get_object_reference(
            'project_budget', 'view_crossovered_budget_line_tree')
        return {
            'name': _('Budget Lines'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'crossovered.budget.lines',
            'view_id': view_id and view_id[1] or False,
            'domain': [('id','in', line_ids)],
        }

    @api.one
    def _compute_budget_amount(self):
        budget_amount = 0.0
        if self.analytic_account_id:
            budget_amount = self.analytic_account_id._compute_recursive_budget_amount()[0]
        self.budget_amount = budget_amount

    budget_amount = fields.Float('Budget', compute='_compute_budget_amount')
