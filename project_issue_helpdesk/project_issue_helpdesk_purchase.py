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
from openerp.exceptions import Warning

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    @api.depends('issue_id')
    @api.one
    def get_account_issue(self):
        account_obj=self.env['account.analytic.account']
        if self.issue_id:
            self.init_onchange_call=self.issue_id.analytic_account_id
        else:
            self.init_onchange_call=account_obj.search([('type','in',['view','template'])])
    @api.onchange('issue_id')
    def get_account(self):
        if self.issue_id.analytic_account_id:
            self.account_analytic_id=self.issue_id.analytic_account_id
        else:
            self.analytic_account=False
    init_onchange_call= fields.Many2many('account.analytic.account',compute="get_account_issue",string='Nothing Display', help='field at view init')
    issue_id=fields.Many2one('project.issue','Issue')

class ProjectIssue(models.Model):
    _inherit = 'project.issue'
    purchase_orde_line=fields.One2many('purchase.order.line','issue_id')