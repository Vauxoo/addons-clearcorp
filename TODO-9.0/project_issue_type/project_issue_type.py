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

class ticket_invoice_type_name (models.Model):
    _name = 'ticket.invoice.type.name'

    name= fields.Char('Name',required='True')
    ticket_type = fields.Selection([('change_request','Change Request'),('service_request','Service Request'),
                                   ('issue','Issue'),('problem','Problem')], 
                                  string='Issue Type', default='issue',required=True)
    
class ticket_invoice_type (models.Model):
    _name = 'ticket.invoice.type'
    
    name= fields.Many2one('ticket.invoice.type.name',required='True')
    warranty = fields.Boolean('Warranty?')
    contract_type_id = fields.Many2one('contract.type')
    
class project_issue(models.Model):
    
    _inherit = 'project.issue'
    
    @api.one
    @api.depends("project_id")
    def _compute_invoice_ticket(self):
        if self.project_id:
                for ticket_kind in self.project_id.analytic_account_id.ticket_invoice_type_ids:
                    if ticket_kind.name == self.issue_type.name:
                        if ticket_kind.warranty:
                            self.invoiced = 'warranty'
                            return False
                        else: 
                            self.invoiced = 'invoice'
                            return True

    issue_type = fields.Many2one('ticket.invoice.type', string='Type')
    invoiced = fields.Selection([
                 ('invoice', 'Invoice'),
                 ('warranty', 'Warranty'),
                 ('2beinvoice', 'To be Invoice'),
                 ('invoiced', 'Invoiced'),
                 ], string = "Invoice", help = "is a invoiced task", compute='_compute_invoice_ticket', store=True)
    
class account_analitic(models.Model):

    _inherit = 'account.analytic.account'
    
    ticket_invoice_type_ids = fields.One2many('ticket.invoice.type','contract_type_id', string='Ticket Type')