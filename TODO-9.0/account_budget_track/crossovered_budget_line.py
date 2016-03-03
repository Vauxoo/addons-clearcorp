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

from openerp import models, fields

class CrossoveredBudgetLine(models.Model):

    _inherit = ['crossovered.budget.lines', 'mail.thread']
    _name = 'crossovered.budget.lines'

    analytic_account_id = fields.Many2one(track_visibility='onchange')
    general_budget_id = fields.Many2one(track_visibility='onchange')
    date_from = fields.Date(track_visibility='onchange')
    date_to = fields.Date(track_visibility='onchange')
    paid_date = fields.Date(track_visibility='onchange')
    planned_amount = fields.Float(track_visibility='onchange')