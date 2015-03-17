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
from openerp.tools.translate import _
from openerp.exceptions import Warning

class IssueInvoiceWizard(models.TransientModel):
    _name='project.issue.helpdesk.invoice.wizard'
    @api.multi
    def get_quantities_issues(self,issue,invoice_id):
        account_obj=self.env['account.analytic.account']
        total_timesheet=0.0
        total_backorder=0.0
        total_expenses=0.0
        for timesheet in issue.timesheet_ids:
            for account_line in timesheet.line_id:
                if not account_line.invoice_id:
                    total_timesheet+=account_obj._get_invoice_price(account_line.account_id,account_line.date,timesheet.start_time,timesheet.end_time,issue.product_id.id,issue.categ_id.id,account_line.unit_amount,timesheet.service_type)
                    account_line.write({'invoice_id':invoice_id})
        for backorder in issue.backorder_ids:
            if backorder.delivery_note_id and backorder.invoice_state!='invoiced' and backorder.state=='done':
                for delivery_note_lines in backorder.delivery_note_id.note_lines:
                    total_backorder+=delivery_note_lines.quantity*delivery_note_lines.price_unit
                    backorder.write({'invoice_state':'invoiced'})
                    backorder.move_lines.write({'invoice_state':'invoiced'})
        for expense_line in issue.expense_line_ids:
            if expense_line.expense_id.state=='done':
                for move_lines in expense_line.expense_id.account_move_id.line_id:
                    for lines in move_lines.analytic_lines:
                        if lines.account_id==expense_line.analytic_account and lines.name==expense_line.name and lines.amount*-1==expense_line.unit_amount and not lines.invoice_id:
                            total_expenses+=lines.amount*-1
                            lines.write({'invoice_id':invoice_id})
        return total_timesheet,total_backorder,total_expenses
    
    @api.multi
    def get_quantities_issues_detail(self,issue,inv):
        account_obj=self.env['account.analytic.account']
        total_expenses=0.0
        for timesheet in issue.timesheet_ids:
            for account_line in timesheet.line_id:
                if not account_line.invoice_id:
                    total_timesheet=0.0
                    total_timesheet=account_obj._get_invoice_price(account_line.account_id,account_line.date,timesheet.start_time,timesheet.end_time,issue.product_id.id,issue.categ_id.id,account_line.unit_amount,timesheet.service_type)
                    if (timesheet.end_time-timesheet.start_time!=0 or total_timesheet!=0):
                        inv.write({'invoice_line':[(0,0, {'name': _(('Service Hours - %s' % str(timesheet.end_time-timesheet.start_time))),'quantity':1,'price_unit':total_timesheet})]})
                    account_line.write({'invoice_id':inv.id})
        for backorder in issue.backorder_ids:
            if backorder.delivery_note_id and backorder.invoice_state!='invoiced' and backorder.state=='done':
                for delivery_note_lines in backorder.delivery_note_id.note_lines:
                    total_backorder=0.0
                    if delivery_note_lines.quantity!=0 or delivery_note_lines.price_unit!=0:
                        inv.write({'invoice_line':[(0,0, {'name': delivery_note_lines.product_id.name,'quantity':delivery_note_lines.quantity,'price_unit':delivery_note_lines.price_unit})]})
                    backorder.write({'invoice_state':'invoiced'})
                    backorder.move_lines.write({'invoice_state':'invoiced'})
        for expense_line in issue.expense_line_ids:
            if expense_line.expense_id.state=='done':
                for move_lines in expense_line.expense_id.account_move_id.line_id:
                    for lines in move_lines.analytic_lines:
                        if lines.account_id==expense_line.analytic_account and lines.name==expense_line.name and lines.amount*-1==expense_line.unit_amount and not lines.invoice_id:
                            total_expenses+=lines.amount*-1
                            lines.write({'invoice_id':inv.id})
        return total_expenses
    
    @api.multi
    def generate_invoices(self,issue_ids,group,line_detailed):
        issue_obj=self.env['project.issue']
        issue_obj=self.env['project.issue']
        invoice_obj=self.env['account.invoice']
        partner_obj=self.env['res.partner']
        partner_group_ids=[]
        branch_group_ids=[]
        branch_issue_ids=[]
        partner_issue_ids=[]
        invoices_list=[]
        total_timesheet=0.0
        total_backorder=0.0
        total_expenses=0.0

        if group==False:
            for issue in issue_ids:
                create_invoice={}
                if issue.branch_id and issue.partner_id:
                    create_invoice['partner_id']=issue.branch_id.id
                    create_invoice['account_id']=issue.branch_id.property_account_receivable.id
                elif not issue.branch_id and issue.partner_id:
                    create_invoice['partner_id']=issue.partner_id.id
                    create_invoice['account_id']=issue.partner_id.property_account_receivable.id
                create_invoice['origin']=_(('Issue #') + issue.issue_number)
                inv=invoice_obj.create(create_invoice)
                invoices_list.append(inv.id)
                if line_detailed==False:
                    total_timesheet,total_backorder,total_expenses=self.get_quantities_issues(issue,inv.id)
                    if total_timesheet+total_backorder!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Issue #') + issue.issue_number ),'quantity':1,'price_unit':total_timesheet+total_backorder})]})
                    if total_expenses!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Expenses of Issue #') + issue.issue_number ),'quantity':1,'price_unit':total_expenses})]})
                elif line_detailed==True:
                    total_expenses=self.get_quantities_issues_detail(issue,inv)
                    if total_expenses!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Expenses of Issue #') + issue.issue_number ),'quantity':1,'price_unit':total_expenses})]})
                inv.write({'issue_ids':[(4,issue.id)]})
        elif group==True:
            for issue in issue_ids:
                if issue.partner_id and issue.branch_id and issue.branch_id.parent_id==issue.partner_id:
                    branch_issue_ids.append(issue.id)
                    if issue.branch_id.id not in branch_group_ids:
                        branch_group_ids.append(issue.branch_id.id)
                elif issue.partner_id and not issue.branch_id:
                    partner_issue_ids.append(issue.id)
                    if issue.partner_id.id not in partner_group_ids:
                        partner_group_ids.append(issue.partner_id.id)
            for partner in partner_group_ids:
                create_invoice={}
                total_timesheet_group=0.0
                total_backorder_group=0.0
                total_expenses_group=0.0
                create_invoice['partner_id']=partner
                create_invoice['account_id']=partner_obj.search([('id','=',partner)]).property_account_receivable.id
                inv=invoice_obj.create(create_invoice)
                invoices_list.append(inv.id)
                issue_partner_ids=issue_obj.search([('id','in',partner_issue_ids),('partner_id','=',partner),('branch_id','=',False)])
                if line_detailed==False:
                    for issue in issue_partner_ids:
                        total_timesheet,total_backorder,total_expenses=self.get_quantities_issues(issue,inv.id)
                        total_timesheet_group+=total_timesheet
                        total_backorder_group+=total_backorder
                        total_expenses_group+=total_expenses
                        inv.write({'issue_ids':[(4,issue.id)]})
                    if total_timesheet_group+total_backorder_group!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Several Issues')),'quantity':1,'price_unit':total_timesheet_group+total_backorder_group})]})
                    if total_expenses_group!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Expenses of Several Issues')),'quantity':1,'price_unit':total_expenses_group})]})
                elif line_detailed==True:
                    for issue in issue_partner_ids:
                        total_expenses=self.get_quantities_issues_detail(issue,inv)
                        total_expenses_group+=total_expenses
                        inv.write({'issue_ids':[(4,issue.id)]})
                    if total_expenses_group!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Expenses of Several Issues')),'quantity':1,'price_unit':total_expenses_group})]})
            for branch in branch_group_ids:
                create_invoice={}
                total_timesheet_group=0.0
                total_backorder_group=0.0
                total_expenses_group=0.0
                create_invoice['partner_id']=branch
                create_invoice['account_id']=partner_obj.search([('id','=',branch)]).property_account_receivable.id
                inv=invoice_obj.create(create_invoice)
                invoices_list.append(inv.id)
                issue_branch_ids=issue_obj.search([('id','in',branch_issue_ids),('branch_id','=',branch),('partner_id','!=',False)])
                if line_detailed==False:
                    for issue in issue_branch_ids:
                        total_timesheet,total_backorder,total_expenses=self.get_quantities_issues(issue,inv.id)
                        total_timesheet_group+=total_timesheet
                        total_backorder_group+=total_backorder
                        total_expenses_group+=total_expenses
                        inv.write({'issue_ids':[(4,issue.id)]})
                    if total_timesheet_group+total_backorder_group!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Several Issues')),'quantity':1,'price_unit':total_timesheet_group+total_backorder_group})]})
                    if total_expenses_group!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Expenses of Several Issues')),'quantity':1,'price_unit':total_expenses_group})]})
                elif line_detailed==True:
                    for issue in issue_branch_ids:
                        total_expenses=self.get_quantities_issues_detail(issue,inv)
                        total_expenses_group+=total_expenses
                        inv.write({'issue_ids':[(4,issue.id)]})
                    if total_expenses_group!=0:
                        inv.write({'invoice_line':[(0,0, {'name': _(('Expenses of Several Issues')),'quantity':1,'price_unit':total_expenses_group})]})
        return invoices_list

    @api.multi
    def validate_issues(self):
        partner_ids=[]
        issue_ids=[]
        model_ids=[]
        issue_obj=self.env['project.issue']
        
        if self.filter=='filter_no':
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False)])
        elif self.filter=='filter_date':
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('create_date', '>=', self.date_from),('create_date', '<=', self.date_to)])
        elif self.filter=='filter_period':
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('create_date', '>=',self.period_from.date_start),('create_date', '<=',self.period_to.date_stop)])
        elif self.filter=='filter_partner':
            for partner in self.partner_ids:
                partner_ids.append(partner.id)
            issue_ids=issue_obj.search(['&','|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),'|',('partner_id','in',partner_ids),('branch_id','in',partner_ids),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False)])
        elif self.filter=='filter_issue':
            for issue in self.issue_ids:
                issue_ids.append(issue.id)
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('id','in',issue_ids)])
        if issue_ids:
            self.issue_invoice_ids=issue_ids
            self.write({'state':'done'})
            return {
                'name': _('Issues to Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
                }
        else:
            raise Warning(_('No pending issues closed for invoicing'))
        
    @api.multi
    def invoice_issues(self):
        if self.issue_invoice_ids:
            invoices_list=self.generate_invoices(self.issue_invoice_ids,self.group_customer,self.line_detailed)
            return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain' : [('id','in',invoices_list),('type','=','out_invoice')],
            'res_model': 'account.invoice',
            'target': 'current',
            'nodestroy': True,
            }
        else:
            raise Warning(_('No pending issues closed for invoicing'))
        
    @api.one
    @api.constrains('date_from','date_to')    
    def _check_filter_date(self):
        if self.filter=='filter_date':
            if self.date_from>self.date_to:
                raise Warning(_('Start Date must be less than End Date'))
    @api.constrains('period_from','period_to')
    def _check_filter_period(self):
        if self.filter=='filter_period':
            if self.period_from.date_start>self.period_to.date_stop:
                raise Warning(_('Start Period must be less than End Period'))
    line_detailed=fields.Boolean( string="Detailed",default=True)
    group_customer=fields.Boolean( string="Group by customer",default=False)
    filter=fields.Selection([('filter_no','No Filter'),('filter_date','Date'),('filter_period','Period'),('filter_partner','Partner'),('filter_issue','Issue')],string="Filter",required=True,default='filter_no')
    date_from=fields.Date(string="Start Date")
    date_to=fields.Date(string="End Date")
    fiscalyear_id=fields.Many2one('account.fiscalyear',string="Fiscal Year")
    period_to= fields.Many2one('account.period',string="End Period")
    period_from= fields.Many2one('account.period',string="Start Period")
    partner_ids= fields.Many2many('res.partner',string="Customers")
    issue_ids=fields.Many2many('project.issue','project_issue_project_issue_wizard_rel',string="Issues")
    issue_invoice_ids=fields.One2many('project.issue',compute='validate_issues',string="Issues")
    state= fields.Selection([('validate','Validate'),('done','Done')], string='State')
    
    _defaults = {
        'state': 'validate'
    }