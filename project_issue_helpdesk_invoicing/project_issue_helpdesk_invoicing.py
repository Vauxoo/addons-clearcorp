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
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    issue_ids=fields.One2many('project.issue','sale_order_id')

class ProjectIssue(models.Model):
    _inherit = 'project.issue'
    @api.v7
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result={}
        domain=[]
        result = super(ProjectIssue, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            domain.append(('type', '!=', 'view'))
            domain.append(('partner_id', '=',partner_id))
            contract_ids = self.pool.get('account.analytic.account').search(cr,uid,[('partner_id','=',partner_id)])
            result.update({'domain':{'analytic_account_id':domain}})
            if contract_ids:
                result['value'].update({'analytic_account_id':contract_ids[0]})
            else:
                result['value'].update({'analytic_account_id':False})
        return result
    
    @api.v7
    def onchange_branch_id(self, cr, uid, ids, branch_id, context=None):
        result={}
        domain=[]
        result = super(ProjectIssue, self).onchange_branch_id(cr, uid, ids, branch_id)
        if branch_id:
            domain.append(('type', '!=', 'view'))
            domain.append(('branch_ids.id', '=',branch_id))
            contract_ids = self.pool.get('account.analytic.account').search(cr,uid,[('branch_ids.id','=',branch_id)])
            result.update({'domain':{'analytic_account_id':domain}})
            if contract_ids:
                result['value'].update({'analytic_account_id':contract_ids[0]})
            else:
                result['value'].update({'analytic_account_id':False})
        return result
        
    sale_order_id=fields.Many2one('sale.order','Sale Order')
    invoice_id=fields.Char(string='Invoice Number',related='sale_order_id.invoice_ids.internal_number')
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_provision=fields.Boolean('Provision Apply')

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    branch_ids=fields.Many2many('res.partner','account_analytic_partner_rel')
    holidays_calendar_id=fields.Many2one('holiday.calendar',string="Holidays Calendar")
    pricelist_ids=fields.One2many('contract.pricelist','contract_id')
    regular_schedule_id=fields.Many2one('resource.calendar',string="Regular Schedule")

class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'
    issue_id=fields.Many2one('project.issue','Issue')
    
    @api.onchange('analytic_account')
    def onchange_analytic_account(self):
        self.issue_id=False
        
class HolidayCalendar(models.Model):
    _name = 'holiday.calendar'
    holiday_ids=fields.One2many('holiday.calendar.date','holidays_calendar_id')
    name=fields.Char(size=256,required=True,string="Calendar Name")
    contract_ids=fields.One2many('account.analytic.account','holidays_calendar_id')
    
class HolidayCalendarDate(models.Model):
    _name = 'holiday.calendar.date'
 
    name=fields.Char(size=256,required=True,string="Holiday Name")
    date=fields.Date(required=True,string="Date")
    notes=fields.Text(string="Notes")
    holidays_calendar_id=fields.Many2one('holiday.calendar',string="Holidays Calendar")
     
class ContractPriceList(models.Model):
    _name = 'contract.pricelist'
    
    @api.onchange('pricelist_line_type')
    def onchange_pricelist_line_type(self):
        if self.pricelist_line_type:
            if self.pricelist_line_type=='category':
                self.product_id=""
            elif self.pricelist_line_type=='product':
                self.categ_id=""
        elif not self.pricelist_line_type:
             self.product_id=""
             self.categ_id=""
             
    @api.constrains('pricelist_line_type')
    def _check_lines(self):
        for line in self:
            if line.pricelist_line_type=='category':
                exist_category=self.search([('categ_id','=', line.categ_id.id),('contract_id','=', line.contract_id.id)])
                if len(exist_category)>1:
                        raise Warning('Contract only allow a line to a single category',['categ_id'])
            elif line.pricelist_line_type=='product':
                exist_product = self.search([('product_id','=', line.product_id.id),('contract_id','=', line.contract_id.id)])
                if len(exist_product)>1:
                    raise Warning('Contract only allow a line to a single product',['product_id'])
        return True
    
    @api.constrains('technical_rate','assistant_rate')
    def _check_rates(self):
        for rate in self:
            if (rate.technical_rate<1.0 or rate.assistant_rate<1.0):
                raise Warning('Rates must be greater or equal to one',['technical_rate','assistant_rate'])
        return True
    
    @api.constrains('overtime_multiplier','holiday_multiplier')
    def _check_multipliers(self):
        for multipliers in self:
            if (multipliers.overtime_multiplier<1.0 or multipliers.holiday_multiplier<1.0):
                raise Warning('Multipliers must be greater or equal to one',['overtime_multiplier','holiday_multiplier'])
        return True
    
    contract_id=fields.Many2one('account.analytic.account',string="Contract")
    pricelist_line_type=fields.Selection([('category','Category'),('product','Product')],string="Pricelist Type")
    categ_id=fields.Many2one('product.category',string="Category Product")
    product_id=fields.Many2one('product.product',string="Product")
    technical_rate=fields.Float(digits=(16,2),required=True,string="Technical Rate")
    assistant_rate=fields.Float(digits=(16,2),required=True,string="Assistant Rate")
    overtime_multiplier=fields.Float(digits=(16,2),required=True,string="Overtime Multiplier")
    holiday_multiplier=fields.Float(digits=(16,2),required=True,string="Holiday Multiplier")
     
    _defaults={
        'technical_rate':0.0,
        'assistant_rate':0.0,
        'overtime_multiplier':1.0
        }
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    @api.depends('invoice_line','quoted_cost','quoted_price','real_cost','real_price','variation_cost','variation_price')
    def get_profitability(self):
        if self.order_ids and not self.order_ids.issue_ids:
            quoted_cost=0.0
            quoted_price=0.0
            real_cost=0.0
            real_price=0.0
            for sale_line in self.order_ids.order_line:
                quoted_cost+=sale_line.product_uom_qty*sale_line.purchase_price
                quoted_price+=sale_line.price_subtotal
            self.quoted_cost=quoted_cost
            self.quoted_price=quoted_price
            for invoice_line in self.invoice_line:
                real_price+=invoice_line.price_subtotal
                if not invoice_line.sale_lines:
                    real_cost+=invoice_line.product_id.standard_price
            self.real_price=real_price
            self.real_cost=quoted_cost+real_cost
            self.expected_margin=self.quoted_price-self.quoted_cost
            self.real_margin=self.real_price-self.real_cost
            self.variation_cost=self.real_cost-self.quoted_cost
            self.variation_price=self.real_price-self.quoted_price
            self.variation_margin=self.real_margin-self.expected_margin
            try:
                self.porcent_variation_cost=(self.real_cost-self.quoted_cost)/self.quoted_cost*100
                self.porcent_variation_price=(self.real_price-self.quoted_price)/self.quoted_price*100
                self.porcent_variation_margin=(self.real_margin-self.expected_margin)/self.expected_margin*100
            except:
                self.porcent_variation_cost=0.0
                self.porcent_variation_price=0.0
                self.porcent_variation_margin=0.0
            
    quoted_cost=fields.Float(compute="get_profitability",digits=(16,2),string="Quoted Cost")
    quoted_price=fields.Float(compute="get_profitability",digits=(16,2),string="Quoted Price")
    expected_margin=fields.Float(compute="get_profitability",digits=(16,2),string="Expected Margin")
    real_cost=fields.Float(compute="get_profitability",digits=(16,2),string="Real Cost")
    real_price=fields.Float(compute="get_profitability",digits=(16,2),string="Real Price")
    real_margin=fields.Float(compute="get_profitability",digits=(16,2),string="Real Margin")
    variation_cost=fields.Float(compute="get_profitability",digits=(16,2),string="Variation Cost")
    variation_price=fields.Float(compute="get_profitability",digits=(16,2),string="Variation Price")
    variation_margin=fields.Float(compute="get_profitability",digits=(16,2),string="Variation Margin")
    porcent_variation_cost=fields.Float(compute="get_profitability",digits=(16,2),string="Variation Cost(%)")
    porcent_variation_price=fields.Float(compute="get_profitability",digits=(16,2),string="Variation Price(%)")
    porcent_variation_margin=fields.Float(compute="get_profitability",digits=(16,2),string="Variation Margin(%)")
    order_ids= fields.Many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id','order_id', 'Sales Order', readonly=True, copy=False, help="This is the list of sales orders that have been generated for this invoice.")
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    sale_lines= fields.Many2many('sale.order.line', 'sale_order_line_invoice_rel', 'invoice_id','order_line_id', 'Sale Lines', readonly=True, copy=False)
