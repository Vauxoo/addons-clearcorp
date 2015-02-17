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
from datetime import datetime
from openerp import models, fields, api, _

class IssueInvoiceWizard(models.TransientModel):
    _name='project.issue.helpdesk.invoice.wizard'
    
#     @api.one
#     @api.constrains('date_from','date_to')    
#     def _check_filter_date(self):
#         if self.filter=='filter_date':
#             if self.date_from>self.date_to:
#                 raise Warning(_('Start Date must be less than End Date'))
#     @api.constrains('period_from','period_to')        
#     def _check_filter_period(self):
#         if self.filter=='filter_period':
#             if self.period_from.date_start>self.period_to.date_stop:
#                 raise Warning(_('Start Period must be less than End Period'))
    
    group=fields.Selection([('group_branch', 'Branch')], string="Group by",required=True,default='group_branch')
    filter=fields.Selection([('filter_no','No Filter'),('filter_date','Date'),('filter_period','Period'),('filter_partner','Partner'),('filter_issue','Issue')],string="Filter",required=True,default='filter_no')
    date_from=fields.Date(string="Start Date")
    date_to=fields.Date(string="End Date")
    fiscalyear_id=fields.Many2one('account.fiscalyear',string="Fiscal Year")
    period_to= fields.Many2one('account.period',string="End Period")
    period_from= fields.Many2one('account.period',string="Start Period")
    partner_ids= fields.Many2many('res.partner',string="Customers")
    issue_ids=fields.Many2many('project.issue','project_issue_project_issue_wizard_rel',string="Issues")