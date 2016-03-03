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
    @api.depends('create_uid')
    @api.one
    def get_department(self):
        if self.create_uid:
            if self.create_uid.employee_id:
                self.department_id=self.create_uid.employee_id.department_id.id
    @api.one
    @api.depends("timesheet_ids")
    def compute_timesheet_total(self):
        total=0.0
        for th in self.timesheet_ids:
            total+=th.amount_unit_calculate
        self.total_timesheets=total
    purchase_orde_line=fields.One2many('purchase.order.line','issue_id')
    is_closed = fields.Boolean(string='Is Closed',related='stage_id.closed',store=True)
    department_id = fields.Many2one('hr.department',compute='get_department',store=True,string='Department')
    total_timesheets= fields.Float(compute="compute_timesheet_total",string="Total Timesheets")
class HrAnaliticTimeSheet(models.Model):
    _inherit = 'hr.analytic.timesheet'
    @api.constrains('start_time','end_time','employee_id','date')
    def _check_overloop_worklogs(self):
        old_timesheet_obj=self.env['hr.analytic.timesheet']
        for timesheet in self:
            overloop_ids=old_timesheet_obj.search([('date','=',timesheet.date),('employee_id','=',timesheet.employee_id.id)])
            for timesheet_old in overloop_ids:
                if timesheet_old.ticket_number!=timesheet.ticket_number:
                    if timesheet.start_time==timesheet.end_time:
                        pass
                    else:
                        if (timesheet.start_time>=timesheet_old.start_time and timesheet.end_time<=timesheet_old.end_time):
                            raise Warning(_('Already exist worklogs register with this range of dates. Ticket Number #%s' %(timesheet_old.ticket_number)))
                        elif (timesheet.start_time<timesheet_old.start_time and timesheet.end_time>timesheet_old.start_time):
                            raise Warning(_('Already exist worklogs register with this range of dates. Ticket Number #%s' %(timesheet_old.ticket_number)))
                        elif (timesheet.start_time<timesheet_old.end_time and timesheet.end_time>timesheet_old.end_time):
                            raise Warning(_('Already exist worklogs register with this range of dates. Ticket Number #%s' %(timesheet_old.ticket_number)))
        return True
    @api.depends('issue_id','task_id')
    @api.one
    def get_account_selected(self):
        account_obj=self.env['account.analytic.account']
        if self.issue_id:
            if self.issue_id.analytic_account_id:
                self.init_onchange_account=self.issue_id.analytic_account_id
                self.account_id=self.issue_id.analytic_account_id
            else:
                self.account_id=False
        elif self.task_id:
            if self.task_id.project_id.analytic_account_id:
                self.init_onchange_account=self.task_id.project_id.analytic_account_id
                self.account_id=self.task_id.project_id.analytic_account_id
            else:
                self.account_id=False
        else:
            self.init_onchange_account=account_obj.search([('type','in',['view','template'])])
            self.account_id=False
    
    @api.depends('account_id')
    @api.one
    def get_factor_invoice_selected(self):
        account_obj=self.env['hr_timesheet_invoice.factor']
        if self.account_id:
            if self.account_id.to_invoice:
                self.init_onchange_factor=self.account_id.to_invoice
                self.to_invoice=self.account_id.to_invoice
            else:
                self.to_invoice=False
        else:
            self.init_onchange_factor=account_obj.search([])
            self.to_invoice=False
    @api.depends('issue_id','task_id')
    @api.one
    def get_account(self):
        if self.issue_id.analytic_account_id:
            self.account_id=self.issue_id.analytic_account_id
        elif self.task_id.project_id.analytic_account_id:
            self.account_id=self.task_id.project_id.analytic_account_id
        else:
            self.analytic_id=False
            
    @api.depends('account_id')
    @api.one
    def get_factor_invoice(self):
        if self.account_id.to_invoice:
            self.to_invoice=self.account_id.to_invoice
        else:
            self.to_invoice=False
    
    @api.depends('issue_id','task_id')
    @api.one
    def get_partner_timesheet(self):
        if self.issue_id:
            if self.issue_id.partner_id:
                self.partner_id=self.issue_id.partner_id.id
            else:
                self.partner_id=False
        elif self.task_id:
            if self.task_id.partner_id.partner_type=='company':
                if self.task_id.partner_id:
                    self.partner_id=self.task_id.partner_id.id
                else:
                    self.partner_id=False
            elif self.task_id.partner_id.partner_type=='branch':
                if self.task_id.partner_id.parent_id:
                    self.partner_id=self.task_id.partner_id.parent_id.id
                else:
                    self.partner_id=False
    @api.depends('issue_id','task_id')
    @api.one
    def get_branch_timesheet(self):
        if self.issue_id:
            if self.issue_id.branch_id:
                self.branch_id=self.issue_id.branch_id.id
            else:
                self.branch_id=False
        elif self.task_id:
            if self.task_id.partner_id.partner_type=='branch':
                if self.branch_id:
                    self.branch_id=self.task_id.partner_id.id
                else:
                    self.branch_id=False

    partner_id = fields.Many2one('res.partner',compute="get_partner_timesheet",store=True,string='Partner')
    branch_id = fields.Many2one('res.partner',compute="get_branch_timesheet",store=True,string='Branch')
    init_onchange_account= fields.Many2many('account.analytic.account',compute="get_account_selected",string='Nothing Display', help='field at view init')
    init_onchange_factor= fields.Many2many('hr_timesheet_invoice.factor',compute="get_factor_invoice_selected",string='Nothing Display', help='field at view init')