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

class Project(models.Model):

    _inherit = 'project.project'

    @api.multi
    def view_crossovered_budget_lines(self):
        return {
            'name': _('Budget Lines'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'crossovered.budget.lines',
            'domain': [('id','in', self.crossovered_budget_line.ids)],
        }

    @api.one
    def _compute_budget_amount(self):
        budget_amount = 0.0
        for line in self.crossovered_budget_line:
            budget_amount += line.practical_amount
        self.budget_amount = budget_amount

    budget_amount = fields.Float('Budget', compute='_compute_budget_amount')