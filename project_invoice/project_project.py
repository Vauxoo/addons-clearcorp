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

class invoice_type (models.Model):
    _name = 'invoice.type'
    
    name= fields.Many2one('ccorp.project.oerp.work.type',required='True')
    invoice = fields.Boolean('Is Invoiced?')
    product_id = fields.Many2one('product.product')
    price= fields.Float('Price')
    contract_type_id = fields.Many2one('contract.type')

class Task(models.Model):

    _inherit = 'project.task'
    
    invoiced = fields.Selection([
                 ('invoice', 'Invoice'),
                 ('not_invoice', 'Not Invoice'),
                 ('tobeinvoice', 'To be Invoice'),
                 ], string = "Invoice", help = "is a invoiced task", default = "tobeinvoice", required = True)
    
    @api.multi
    def send_email(self):
         return {'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'view_type': 'form',
                'view_mode': 'form',
                'nodestroy': True,
                'target': 'new',
                'flags': {'form': {'action_buttons': True}}
                }
         
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
            line_invoice_type = project.invoice_type_id.search([('name','=',task.kind_task_id.name),('invoice','=', True),('contract_type_id','=',project_id.analytic_account_id.id)])
            if line_invoice_type.invoice:
                return True
            else:
                return False
        
    def get_contract_price(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            cost= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('invoice','=', True),('contract_type_id','=',project_id.analytic_account_id.id)])
            cost= cost.price * task.effective_hours
        else: 
            cost= project.fix_price_to_invoice
        return cost
    
    def get_product(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            product= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('invoice','=', True),('contract_type_id','=',project_id.analytic_account_id.id)])
            return product.product_id.id
    
    def get_price_hour(self, task, project_id):
        project = self.env['account.analytic.account']
        project = project.search([('id', '=', project_id.analytic_account_id.id)])
        if project.invoice_on_timesheets:
            price_hour= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('invoice','=', True),('contract_type_id','=',project_id.analytic_account_id.id)])
            return price_hour.price

    def get_contract(self, task, project_id):
        project = self.env['account.analytic.account']
        project= project.invoice_type_id.search([('name','=',task.kind_task_id.name),('invoice','=', True),('contract_type_id','=',project_id.analytic_account_id.id)])
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

    @api.multi
    def action_invoice_create(self, data, journal_id=False, group=False, account=False, date_invoice=False):
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
                    if self.get_invoce(task, task.project_id):
                        invoice_line_vals={
                                           'invoice_id': invoice_create_id.id,
                                           'product_id': self.get_product(task, task.project_id),
                                           'name': task.name,
                                           'account_id': self.get_partner_account(key),
                                           'account_analytic_id': self.get_contract(task, task.project_id),
                                           'quantity': task.effective_hours,
                                           'price_unit':self.get_price_hour(task, task.project_id),
                                           'price_subtotal':self.get_contract_price(task, task.project_id),
                                           }
                        invoice_line_create_id = invoice_line_obj.create(invoice_line_vals)
                        task.invoiced = 'invoice'
        return True

class account_analitic(models.Model):

    _inherit = 'account.analytic.account'
    
    invoice_type_id= fields.One2many('invoice.type', 'contract_type_id', string='Invoice Type', required=True)
   