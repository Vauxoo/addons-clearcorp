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
    @api.v7
    def create(self, cr, uid, vals, context=None):
        if 'issue_type' in vals and vals.get('issue_type'):
            if vals.get('issue_type')=='preventive check':
                raise Warning(_('You can not create an issue of preventive check type from this screen'))
        return super(ProjectIssue, self).create(cr, uid, vals, context)
    @api.v7
    def write(self, cr, uid, ids, vals, context=None):
        if 'issue_type' in vals and vals.get('issue_type'):
           if vals.get('issue_type')=='preventive check':
                raise Warning(_('You can not create an issue of preventive check type from this screen'))
        return super(ProjectIssue, self).write(cr, uid, ids, vals, context)
    
    purchase_orde_line=fields.One2many('purchase.order.line','issue_id')
    is_closed = fields.Boolean(string='Is Closed',related='stage_id.closed',store=True)
    
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
    