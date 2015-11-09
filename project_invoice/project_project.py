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

from openerp import models, fields, api
from datetime import date
import time

class invoice_type (models.Model):
    _name = 'invoice.type'
    
    name= fields.Many2one('ccorp.project.oerp.work.type',required='True')
    invoice = fields.Boolean('Is Invoiced?')
    product_price = fields.Boolean('Use product price')
    product_id = fields.Many2one('product.product')
    price= fields.Float('Price')
    contract_type_id = fields.Many2one('contract.type')
    acc_analytic_qty_grp_id = fields.Many2one('account.analytic.quantity_max_group', string='Prepay Hours')
    
    @api.one
    @api.onchange("name")
    def onchange_name(self):
        self.product_id = self.name.product_id
        return True

"""class ticket_invoice_type (models.Model):
    _name = 'ticket.invoice.type'
    
    name= fields.Char('Name',required='True')
    warranty = fields.Boolean('Warranty?')
    ticket_type = fields.Selection([('change_request','Change Request'),('service_request','Service Request'),
                                   ('issue','Issue'),('problem','Problem')], 
                                  string='Issue Type', default='issue',required=True)
    contract_type_id = fields.Many2one('contract.type')"""

class Task(models.Model):

    _inherit = 'project.task'
    
    invoiced = fields.Selection([
                 ('invoice', 'Invoice'),
                 ('not_invoice', 'Not Invoice'),
                 ('tobeinvoice', 'To be Invoice'),
                 ], string = "Invoice", help = "is a invoiced task", compute='_compute_invoice', store=True)
    
    @api.one
    @api.depends("ticket_ids")
    def _compute_invoice_ticket(self):
        if self.project_id:
            for ticket_id in self.ticket_ids:
                if self.project_id == ticket_id.project_id:
                    for ticket_kind in self.project_id.analytic_account_id.ticket_invoice_type_ids:
                        if ticket_kind.name == ticket_id.issue_type:
                            if ticket_kind.warranty:
                                self.invoiced = 'not_invoice'
                                return False
                            else: 
                                self.invoiced = 'tobeinvoice'
                                return True   
    
    
    @api.one
    @api.depends("kind_task_id")
    def _compute_invoice(self):
        if self.ticket_ids:
            if self.project_id:
                for ticket_id in self.ticket_ids:
                    if self.project_id == ticket_id.project_id:
                        for ticket_kind in self.project_id.analytic_account_id.ticket_invoice_type_ids:
                            if ticket_kind.name == ticket_id.issue_type:
                                if ticket_kind.warranty:
                                    self.invoiced = 'not_invoice'
                                    return False
                                else: 
                                    self.invoiced = 'tobeinvoice'
                                    return True
        else:
            if self.project_id:
                for kind in self.project_id.analytic_account_id.invoice_type_id:
                    if kind.name == self.kind_task_id:
                        if kind.invoice:
                            self.invoiced = 'tobeinvoice'
                            return True
                        if self.feature_id.invoiceable:
                                self.invoiced = 'tobeinvoice'
                                return True
                        else:
                                self.invoiced = 'not_invoice'
                                return False
                         
                      
    @api.multi
    def split_task(self):
        task_copy = self.copy()
        return {'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_type': 'form',
                'view_mode': 'form',
                'nodestroy': True,
                'res_id': task_copy.id,
                'target': 'new',
                }

    def get_invoce(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            line_invoice_type = project.invoice_type_id.search([('name','=',task.kind_task_id.name),('contract_type_id','=',project_id.analytic_account_id.id)])
            if line_invoice_type.invoice:
                return True
            else:
                return False
        
    def get_contract_price(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            cost= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('contract_type_id','=',project_id.analytic_account_id.id)])
            cost= cost.price * task.planned_hours
        else: 
            cost= project.fix_price_to_invoice
        return cost
    
    def get_product(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            product= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('contract_type_id','=',project_id.analytic_account_id.id)])
            return product.product_id.id
    
    def get_price_hour(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            price_hour= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('contract_type_id','=',project_id.analytic_account_id.id)])
            return price_hour.price

    def get_contract(self, task, project_id):
        project = self.env['account.analytic.account']
        project= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('contract_type_id','=',project_id.analytic_account_id.id)])
        if project:
            project = project.search([('id', '=', project_id.analytic_account_id.id)])
            return project.id
    
    def get_contract_partner_id(self, key):
        project = self.env['project.project']
        project= project.search([('id','=',key)])
        if project:
            partner = project.partner_id.id
            return partner
    
    def get_partner_account(self, key):
        project = self.env['project.project']
        partner = self.env['res.partner']
        project= project.search([('id','=',key)])
        if project:
            partner = partner.search([('id','=',project.partner_id.id)])
            return partner.property_account_receivable.id
        
    def get_contract_currency_id(self, key):
        project = self.env['project.project']
        project= project.search([('id','=',key)])
        if project:
            currency = project.analytic_account_id.currency_id.id
            return currency
        
    def get_product_price(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            product_price= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('product_price','=', True),('contract_type_id','=',project_id.analytic_account_id.id)])
            return product_price.product_price

    @api.multi
    def action_invoice_create(self, data, journal_id=False, account=False, date_invoice=False):
        cost=0
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        task_obj = self.env['project.task']
        for key, values in data.iteritems():
            invoice_vals = {
                         'partner_id':  self.get_contract_partner_id(key),
                         'journal_id': journal_id,
                         'account_id': self.get_partner_account(key),
                         'currency_id': self.get_contract_currency_id(key),
                         'date_invoice': date_invoice,
                         }
            invoice_create_id = invoice_obj.create(invoice_vals)
            for value in values:
                task = task_obj.search([('id', '=', value)])
                if task.invoiced == 'tobeinvoice':
                        invoice_line_vals={
                                           'invoice_id': invoice_create_id.id,
                                           'product_id': self.get_product(task, task.project_id),
                                           'name': task.name,
                                           'account_id': self.get_partner_account(key),
                                           'account_analytic_id': self.get_contract(task, task.project_id),
                                           'quantity': task.effective_hours,
                                           }
                        if not self.get_product_price(task, task.project_id):
                            invoice_line_vals['price_unit']= self.get_price_hour(task, task.project_id)
                            invoice_line_vals['price_subtotal']= self.get_contract_price(task, task.project_id)
                            invoice_line_create_id = invoice_line_obj.create(invoice_line_vals)
                        else:
                            draft_invoice_line = self.env['account.invoice.line']
                            x = draft_invoice_line.product_id_change(self.get_product(task, task.project_id), False, False, False, False, self.get_contract_partner_id(key) )
                            invoice_line_vals['price_unit']= x['value']['price_unit']
                            invoice_line_vals['price_subtotal']= invoice_line_vals['price_unit'] * task.planned_hours
                            invoice_line_create_id = invoice_line_obj.create(invoice_line_vals)
                        
                task.invoiced = 'invoice'
        return True
    
class Feature(models.Model):
    
    _inherit = 'ccorp.project.scrum.feature'
    
    invoiceable= fields.Boolean('To be invoice?')
    state= fields.Selection([('draft', 'New'), ('open', 'In Progress'), 
                             ('cancelled', 'Cancelled'), ('done', 'Done'), ('quote_pending', 'Quote Pending')],
                             'Status', required=True)
    sale_order_id = fields.Many2one('sale.order')
    
    @api.multi
    def generate_so(self, feat, sale_order_id=False):
        today = date.today().strftime('%Y-%m-%d')
        sum_cost=0
        sum_hours=1
        sale_order_obj = self.env['sale.order']
        sale_order_line_obj = self.env['sale.order.line']
        for hour in feat.hour_ids:
            if not feat.project_id.analytic_account_id.invoice_type_id.search([('name','=', hour.work_type_id.name)]).product_price:
                price= feat.project_id.analytic_account_id.invoice_type_id.search([('name','=', hour.work_type_id.name)]).price * hour.expected_hours
            else:
                product_id= feat.project_id.analytic_account_id.invoice_type_id.search([('name','=', hour.work_type_id.name)]).product_id
                product = feat.env['product.product'].browse(product_id.id)
                price= product[0].lst_price * hour.expected_hours
            sum_cost = sum_cost + price
         
        if not sale_order_id:   
            #create the sale order
            sale_order_vals = {
                             'partner_id':  feat.project_id.partner_id.id,
                             'date_order': today,
                             'project_id': feat.project_id.analytic_account_id.id
                             }
            sale_order_create_id = sale_order_obj.create(sale_order_vals)
            
            #create sale order line
            if feat.description:
                saleorder_line_vals={
                                         'order_id': sale_order_create_id.id,
                                         'name': feat.description, 
                                         'product_uom_qty': sum_hours,
                                         'price_unit':sum_cost,
                                         'price_subtotal':sum_cost,
                                        }
            else:
                saleorder_line_vals={
                                         'order_id': sale_order_create_id.id,
                                         'name': feat.name, 
                                         'product_uom_qty': sum_hours,
                                         'price_unit':sum_cost,
                                         'price_subtotal':sum_cost,
                                        }
            saleorder_line_create_id = sale_order_line_obj.create(saleorder_line_vals)
            feat.state = 'quote_pending'
            feat.sale_order_id = sale_order_create_id
            return sale_order_create_id
        else:
            if feat.description:
                saleorder_line_vals={
                                         'order_id': sale_order_id.id,
                                         'name': feat.description, 
                                         'product_uom_qty': sum_hours,
                                         'price_unit':sum_cost,
                                         'price_subtotal':sum_cost,
                                        }
            else:
                saleorder_line_vals={
                                         'order_id': sale_order_id.id,
                                         'name': feat.name, 
                                         'product_uom_qty': sum_hours,
                                         'price_unit':sum_cost,
                                         'price_subtotal':sum_cost,
                                        }
            saleorder_line_create_id = sale_order_line_obj.create(saleorder_line_vals)
            feat.state = 'quote_pending'
            feat.sale_order_id = sale_order_id
            return sale_order_id
    
    _defaults = {'state': 'draft'}

class account_analitic(models.Model):

    _inherit = 'account.analytic.account'
    
    invoice_type_id= fields.One2many('invoice.type', 'contract_type_id', string='Invoice Type', required=True)
    #ticket_invoice_type_ids = fields.One2many('ticket.invoice.type', 'contract_type_id', string='Ticket Type')
    acc_analytic_qty_grp_ids = fields.One2many('account.analytic.quantity_max_group','analitic_account_id')
    
class account_analytic_invoice_line(models.Model):

    _inherit = 'account.analytic.invoice.line'
    
    partner_id = fields.Many2one('res.partner',string='Supplier' )
    amount_po = fields.Float('Price')
    
   