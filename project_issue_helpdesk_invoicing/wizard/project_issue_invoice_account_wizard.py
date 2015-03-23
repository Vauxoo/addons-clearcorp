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
    _name='project.issue.invoice.account.wizard'
    @api.multi
    def validate_issues(self):
        partner_ids=[]
        issue_ids=[]
        model_ids=[]
        issue_obj=self.env['project.issue']
        if self.filter=='filter_no':
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('analytic_account_id','=',self.account_id.id)])
        elif self.filter=='filter_date':
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('create_date', '>=', self.date_from),('create_date', '<=', self.date_to),('analytic_account_id','=',self.account_id.id)])
        elif self.filter=='filter_period':
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('create_date', '>=',self.period_from.date_start),('create_date', '<=',self.period_to.date_stop),('analytic_account_id','=',self.account_id.id)])
        elif self.filter=='filter_partner':
            for partner in self.partner_ids:
                partner_ids.append(partner.id)
            issue_ids=issue_obj.search(['&','|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),'|',('partner_id','in',partner_ids),('branch_id','in',partner_ids),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_id','=',False),('analytic_account_id','=',self.account_id.id)])
        elif self.filter=='filter_issue':
            for issue in self.issue_ids:
                issue_ids.append(issue.id)
            issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('analytic_account_id','=',self.account_id),('invoice_id','=',False),('id','in',issue_ids),('analytic_account_id','=',self.account_id.id)])
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
        
    @api.multi
    def invoice_issues(self):
        wizard_obj=self.env['project.issue.helpdesk.invoice.wizard']
        invoices_list=[]
        if self.issue_invoice_ids:
            invoices_list=wizard_obj.generate_invoices(self.issue_invoice_ids,self.group_customer,self.line_detailed)
            view_ref = self.env['ir.model.data'].get_object_reference('account.invoice', 'action_invoice_tree1')
            view_id = view_ref[1] if view_ref else False
            return {
               'type': 'ir.actions.act_window',
               'name': _('Customer Invoice'),
               'res_model': 'account.invoice',
               'view_type': 'form',
               'view_mode': 'tree,form,calendar,graph',
               'view_id': view_id,
               'target': 'current',
               'domain': {[('type','=','out_invoice')]},
               'context': {'default_partner_id': client_id}
               }

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
        
    account_id= fields.Many2one('account.analytic.account',string="Account")
    line_detailed=fields.Boolean( string="Detailed",default=True)
    group_customer=fields.Boolean( string="Group by customer",default=False)
    filter=fields.Selection([('filter_no','No Filter'),('filter_date','Date'),('filter_period','Period'),('filter_partner','Partner'),('filter_issue','Issue')],string="Filter",required=True,default='filter_no')
    date_from=fields.Date(string="Start Date")
    date_to=fields.Date(string="End Date")
    fiscalyear_id=fields.Many2one('account.fiscalyear',string="Fiscal Year")
    period_to= fields.Many2one('account.period',string="End Period")
    period_from= fields.Many2one('account.period',string="Start Period")
    partner_ids= fields.Many2many('res.partner',string="Customers")
    issue_ids=fields.Many2many('project.issue','project_issue_helpdesk_account_wizard_rel',string="Issues")
    issue_invoice_ids=fields.One2many('project.issue',compute='validate_issues',string="Issues")
    state= fields.Selection([('validate','Validate'),('done','Done')], string='State')
    _defaults = {
        'state': 'validate',
        'account_id': lambda self, cr, uid, context: context.get('active_id', False)
    }