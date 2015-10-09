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
from datetime import date,datetime
from openerp import models, fields, api, _
from openerp.tools.translate import _
from openerp.exceptions import Warning
import time
from dateutil.relativedelta import relativedelta

class IssueInvoiceWizard(models.TransientModel):
    _name='project.issue.invoice.account.wizard'
    def create_invoice_lines(self,invoice_dict,sales):
        task_obj=self.pool.get('project.task')
        invoice_obj=self.env['account.invoice']
        sale_line=self.env['sale.order.line']
        user = self.env['res.users'].browse(self._uid)
        invoices_list=[]
        invoices_list_extra=[]
        count_lines=1
        first_line_extra=0
        count_lines_extra=1
        limit_lines=user.company_id.maximum_invoice_lines
        inv=invoice_obj.create(invoice_dict)
        sales.write({'invoice_ids':[(4,inv.id)]})
        invoices_list.append(inv.id)
        for sale in sales:
            for line in sale.order_line:
                if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                    line_id = line.invoice_line_create()
                    if count_lines<=limit_lines or limit_lines==0 or limit_lines==-1:
                        inv.write({'invoice_line':[(4,line_id[0])]})
                        count_lines+=1
                    else:
                        inv=invoice_obj.create(invoice_dict)
                        sale.write({'invoice_ids':[(4,inv.id)]})
                        invoices_list.append(inv.id)
                        count_lines=1
                        inv.write({'invoice_line':[(4,line_id[0])]})
                        count_lines+=1
            for task in sale.task_ids:
                if not task.invoice_id:
                    if task.is_closed==False:
                        raise Warning(_('Task pending for close in the sale order %s' %sale.name))
                    else:
                        account_id=sale.order_line[0].product_id.property_account_income.id
                        if not account_id:
                            account_id = sale.order_line[0].product_id.categ_id.property_account_income_categ.id
                            if not account_id:
                                prop = self.env['ir.property'].get('property_account_income_categ', 'product.category')
                                account_id = prop and prop.id or False
                        invoice_line={
                                   'name': task.name,
                                   'quantity':1,
                                   'price_unit':0,
                                   'discount':sale.project_id.to_invoice.factor,
                                   'account_analytic_id':sale.project_id.id,
                                   'account_id': account_id,
                                   'sequence':100
                                   }
                        if task.extra==True:
                            if first_line_extra==0:
                                inv2=invoice_obj.create(invoice_dict)
                                invoices_list_extra.append(inv2.id)
                                first_line_extra=+1
                            if count_lines_extra<=limit_lines or limit_lines==0 or limit_lines==-1:
                                inv2.write({'invoice_line':[(0,0,invoice_line)]})
                                count_lines+=1
                            else:
                                inv2=invoice_obj.create(invoice_dict)
                                sales.write({'invoice_ids':[(4,inv2.id)]})
                                invoices_list_extra.append(inv2.id)
                                count_lines=1
                                inv2.write({'invoice_line':[(0,0,invoice_line)]})
                                count_lines+=1
                        for timesheet in task.timesheet_ids:
                            for account_line in timesheet.line_id:
                                if not account_line.invoice_id:
                                    if task.extra==True:
                                        account_line.write({'invoice_id':inv2.id})
                                    else:
                                        account_line.write({'invoice_id':inv.id})
                        for backorder in task.backorder_ids:
                            if backorder.delivery_note_id and backorder.picking_type_id.code=='outgoing' and backorder.delivery_note_id.state=='done' and backorder.invoice_state!='invoiced' and backorder.state=='done':
                                backorder.write({'invoice_state':'invoiced'})
                                backorder.move_lines.write({'invoice_state':'invoiced'})
                                backorder.delivery_note_id.write({'state':'invoiced'})
                                if task.extra==True:
                                    for invoice in invoices_list_extra:
                                        backorder.delivery_note_id.write({'invoice_ids':[(4,invoice)]})
                                else:
                                    for invoice in invoices_list:
                                         backorder.delivery_note_id.write({'invoice_ids':[(4,invoice)]})
                        for expense_line in task.expense_line_ids:
                            if expense_line.expense_id.state=='done' or expense_line.expense_id.state=='paid':
                                for move_lines in expense_line.expense_id.account_move_id.line_id:
                                    for lines in move_lines.analytic_lines:
                                        if lines.account_id==expense_line.analytic_account and lines.name==expense_line.name and lines.unit_amount==expense_line.unit_quantity and (lines.amount*-1/lines.unit_amount)==expense_line.unit_amount and not lines.invoice_id:
                                            if task.extra==True:
                                                lines.write({'invoice_id':inv2.id})
                                            else:
                                                lines.write({'invoice_id':inv.id})
                        if task.extra==True:
                            task_obj.write(self._cr,self._uid,task.id,{'invoice_id':inv2.id})
                        else:
                            task_obj.write(self._cr,self._uid,task.id,{'invoice_id':inv.id})
        return invoices_list+invoices_list_extra
    @api.multi
    def generate_invoice_sale_order(self, sale_orders):
        result={}
        invoice_sale=[]
        order_obj=self.pool.get('sale.order')
        for sale in sale_orders:
            if sale.partner_id and sale.partner_id.property_payment_term.id:
                pay_term = sale.partner_id.property_payment_term.id
            else:
                pay_term = False
            inv = {
                'name': sale.client_order_ref or '',
                'origin': sale.name,
                'type': 'out_invoice',
                'reference': "P%dSO%d" % (sale.partner_id.id, sale.id),
                'account_id': sale.partner_id.property_account_receivable.id,
                'partner_id': sale.partner_invoice_id.id,
                'currency_id' : sale.pricelist_id.currency_id.id,
                'comment': sale.note,
                'payment_term': pay_term,
                'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id,
                'user_id': sale.user_id and sale.user_id.id or False,
                'company_id': sale.company_id and sale.company_id.id or False,
                'date_invoice': fields.date.today()
            }
            invoice_sale+=self.create_invoice_lines(inv,sale)
            sale.write({'state':'progress'})
        return invoice_sale
    @api.multi
    def generate_preventive_check(self, contracts):
        issue_obj=self.env['project.issue']
        invoice_obj=self.env['account.invoice']
        account_payment_term_obj = self.env['account.payment.term']
        currency_obj = self.env['res.currency']
        ctx = dict(self._context)
        invoices_list=[]
        for contract in contracts:
            account_id=contract.product_id.property_account_income.id or contract.product_id.categ_id.property_account_income_categ.id
            if contract.invoice_partner_type=='branch':
                for branch in contract.branch_ids:
                    if branch.property_product_pricelist:
                        if contract.pricelist_id.currency_id.id != branch.property_product_pricelist.currency_id.id:
                            import_currency_rate=contract.pricelist_id.currency_id.get_exchange_rate(branch.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    else:
                        if contract.pricelist_id.currency_id.id != contract.company_id.currency_id.id:
                            import_currency_rate=contract.pricelist_id.currency_id.get_exchange_rate(contract.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    date_due = False
                    if branch.property_payment_term:
                        pterm_list= account_payment_term_obj.compute(branch.property_payment_term.id, value=1,date_ref=time.strftime('%Y-%m-%d'))
                        if pterm_list:
                            pterm_list = [line[0] for line in pterm_list]
                            pterm_list.sort()
                            date_due = pterm_list[-1]
                    invoice={
                            'partner_id':branch.id,
                            'company_id':contract.company_id.id,
                            'payment_term':branch.property_payment_term.id,
                            'account_id':branch.property_account_receivable.id,
                            'name':contract.name,
                            'currency_id':branch.property_product_pricelist.currency_id.id or contract.company_id.currency_id.id,
                            'fiscal_position':branch.property_account_position.id,
                            'date_due':date_due
                            }
                    ctx = dict(self._context)
                    ctx['lang']=branch.lang
                    ctx['force_company']=contract.company_id.id
                    ctx['company_id']=contract.company_id.id
                    self = self.with_context(ctx)
                    inv=invoice_obj.create(invoice)
                    invoices_list.append(inv.id)
                    invoice_line={
                                  'product_id':contract.product_id.id,
                                  'name': contract.name,
                                  'quantity':1,
                                  'price_unit':contract.amount_preventive_check*import_currency_rate,
                                  'discount':contract.to_invoice.factor,
                                  'account_analytic_id': contract.id,
                                  'invoice_line_tax_id':[(6, 0, [tax.id for tax in contract.product_id.taxes_id])],
                                  'account_id':account_id,
                                  'reference':_('Contract')
                                  }
                    inv.write({'invoice_line':[(0,0,invoice_line)]})
            elif contract.invoice_partner_type=='customer':
                date_due = False
                if contract.partner_id.property_product_pricelist:
                    if contract.pricelist_id.currency_id.id != contract.partner_id.property_product_pricelist.currency_id.id:
                        import_currency_rate=contract.pricelist_id.currency_id.get_exchange_rate(contract.partner_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                    else:
                        import_currency_rate = 1
                else:
                    if contract.pricelist_id.currency_id.id != contract.company_id.currency_id.id:
                        import_currency_rate=contract.pricelist_id.currency_id.get_exchange_rate(contract.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                    else:
                        import_currency_rate = 1
                if contract.partner_id.property_payment_term:
                    pterm_list= account_payment_term_obj.compute(contract.partner_id.property_payment_term.id, value=1,date_ref=time.strftime('%Y-%m-%d'))
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        date_due = pterm_list[-1]
                invoice={
                       'partner_id':contract.partner_id.id,
                       'company_id':contract.company_id.id,
                       'payment_term':contract.partner_id.property_payment_term.id,
                       'account_id':contract.partner_id.property_account_receivable.id,
                       'name':contract.name,
                       'currency_id':contract.company_id.currency_id.id,
                       'fiscal_position':contract.partner_id.property_account_position.id,
                       'date_due':date_due
                       }
                ctx = dict(self._context)
                ctx['lang']=contract.partner_id.lang
                ctx['force_company']=contract.company_id.id
                ctx['company_id']=contract.company_id.id
                self = self.with_context(ctx)
                inv=invoice_obj.create(invoice)
                invoices_list.append(inv.id)
                invoice_line={
                              'product_id':contract.product_id.id,
                              'name': contract.name,
                              'quantity':1,
                              'price_unit':contract.amount_preventive_check*import_currency_rate,
                              'discount':contract.to_invoice.factor,
                              'account_analytic_id': contract.id,
                              'invoice_line_tax_id':[(6, 0, [tax.id for tax in contract.product_id.taxes_id])],
                              'account_id':account_id,
                              'reference':_('Contract')
                              }
                inv.write({'invoice_line':[(0,0,invoice_line)]})
            for issue in issue_obj.search([('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('analytic_account_id','=',contract.id)]):
                inv.write({'issue_ids':[(4,issue.id)]})
        return invoices_list
    
    def get_next_execute_preventive_check(self,contract):
        next_date_execute=False
        if contract.preventive_check_invoice_date:
            if contract.preventive_check_interval_type=='days':
                next_date_execute=datetime.strptime(contract.preventive_check_invoice_date, '%Y-%m-%d') + relativedelta(days=+contract.preventive_check_interval_number)
            elif contract.preventive_check_interval_type=='weeks':
                next_date_execute=datetime.strptime(contract.preventive_check_invoice_date, '%Y-%m-%d') + relativedelta(weeks=+contract.preventive_check_interval_number)
            elif contract.preventive_check_interval_type=='months':
                next_date_execute=datetime.strptime(contract.preventive_check_invoice_date, '%Y-%m-%d') + relativedelta(months=+contract.preventive_check_interval_number)
        else:
            next_date_execute=False
        return next_date_execute.date()
    @api.multi
    def validate_contracts(self):
        account_analytic_list=[]
        partner_ids=[]
        issue_ids=[]
        model_ids=[]
        issue_obj=self.env['project.issue']
        contracts=self.env['account.analytic.account'].search(['|',('invoice_on_timesheets','=',True),('charge_expenses','=',True),('id','in',self._context.get('active_ids'))])
        if contracts:
            if self.filter=='filter_no':
                issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('analytic_account_id','in',self._context.get('active_ids', False))],order='categ_id asc,product_id asc,create_date asc')
            elif self.filter=='filter_date':
                issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('create_date', '>=', self.date_from),('create_date', '<=', self.date_to),('analytic_account_id','in',self._context.get('active_ids', False))],order='categ_id asc,product_id asc,create_date asc')
            elif self.filter=='filter_period':
                issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('create_date', '>=',self.period_from.date_start),('create_date', '<=',self.period_to.date_stop),('analytic_account_id','in',self._context.get('active_ids', False))],order='categ_id asc,product_id asc,create_date asc')
            elif self.filter=='filter_partner':
                for partner in self.partner_ids:
                    partner_ids.append(partner.id)
                issue_ids=issue_obj.search(['&','|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),'|',('partner_id','in',partner_ids),('branch_id','in',partner_ids),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('analytic_account_id','in',self._context.get('active_ids', False))],order='categ_id asc,product_id asc,create_date asc')
            elif self.filter=='filter_issue':
                for issue in self.issue_ids:
                    issue_ids.append(issue.id)
                issue_ids=issue_obj.search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('id','in',issue_ids),('analytic_account_id','in',self._context.get('active_ids', False))],order='categ_id asc,product_id asc,create_date asc')
            self.issue_invoice_ids=issue_ids
        else:
            self.issue_invoice_ids=False
        self.write({'state':'done'})
        return {
            'name': _('Issues to Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context':self._context
            }
        
    @api.multi
    def invoice_contracts(self):
        wizard_obj=self.env['project.issue.helpdesk.invoice.wizard']
        invoices_list_issues=[]
        issue_list=[]
        invoice_sale_list=[]
        invoice_preventive_check_list=[]
        if self.issue_invoice_ids:
            for issue in self.issue_invoice_ids:
                issue_list.append(issue.id)
            invoices_list_issues=wizard_obj.generate_invoices(self.issue_invoice_ids,issue_list,self.group_customer,self.line_detailed)
        if self.sale_order_invoice_ids:
            invoice_sale_list=self.generate_invoice_sale_order(self.sale_order_invoice_ids)
        if self.contract_preventive_check_ids:
            invoice_preventive_check_list=self.generate_preventive_check(self.contract_preventive_check_ids)
                
        result = self.env['ir.model.data'].get_object_reference('account', 'action_invoice_tree1')
        id = result and result[1] or False
        act_win = self.env['ir.actions.act_window'].search_read([('id','=',id)])[0]
        act_win['domain']=[('id','in',invoices_list_issues+invoice_sale_list+invoice_preventive_check_list),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win
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
    @api.onchange('filter')
    def get_account_issues(self):
        contracts=self.env['account.analytic.account'].search(['|',('invoice_on_timesheets','=',True),('charge_expenses','=',True),('id','in',self._context.get('active_ids'))])
        if contracts:
            if self.filter=='filter_issue':
                self.init_onchange_call=self.env['project.issue'].search(['|','|',('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('analytic_account_id','in',self._context.get('active_ids', False))])
            else:
                self.issue_ids=False
        else:
            self.issue_ids=False
    @api.onchange('state')
    def get_account(self):
        if 'active_ids' in self._context and self._context.get('active_ids'):
            self.sale_order_invoice_ids=self.env['sale.order'].search([('project_id','in',self._context.get('active_ids', False)),('state','=','manual')])
            self.contract_preventive_check_ids=self.env['account.analytic.account'].search([('id','in',self._context.get('active_ids', False)),('invoice_preventive_check','!=',False)])
    line_detailed=fields.Boolean(string="Product lines separate service lines",default=True)
    group_customer=fields.Boolean( string="Group by customer",default=True)
    filter=fields.Selection([('filter_no','No Filter'),('filter_date','Date'),('filter_period','Period'),('filter_partner','Partner'),('filter_issue','Issue')],string="Filter",required=True,default='filter_no')
    date_from=fields.Date(string="Start Date")
    date_to=fields.Date(string="End Date")
    fiscalyear_id=fields.Many2one('account.fiscalyear',string="Fiscal Year")
    period_to= fields.Many2one('account.period',string="End Period")
    period_from= fields.Many2one('account.period',string="Start Period")
    partner_ids= fields.Many2many('res.partner',string="Customers")
    init_onchange_call= fields.Many2many('project.issue',compute="get_account_issues",string='Nothing Display', help='field at view init')
    issue_ids=fields.Many2many('project.issue',relation='project_issue_helpdesk_account_wizard_rel',string="Issues")
    issue_invoice_ids=fields.Many2many('project.issue',relation='project_issue_to_invoice_account_wizard_rel',string="Issues")
    sale_order_invoice_ids=fields.Many2many('sale.order',relation='sale_order_to_invoice_account_wizard_rel',string="Sale Orders")
    state= fields.Selection([('validate','Validate'),('done','Done')], string='State')
    contract_preventive_check_ids=fields.Many2many('account.analytic.account',relation='account_analytic_invoice_account_wizard_rel',string="Contracts")
    _defaults = {
        'state': 'validate'
    }