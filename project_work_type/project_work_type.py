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

class WorkType(osv.Model):
    
    _name = 'ccorp.project.oerp.work.type'
    
    _order = 'sequence'
    
    name= fields.Char('name', size=128, required=True)
    product_id= fields.Many2one('product.product', string='Product', required='True')
    sequence= fields.Integer('Sequence', required=True)
    column_number= fields.Integer('Column Number', required=True),
    
class Task(osv.Model):
    
    _inherit = 'project.task'
    
    invoiced = fields.Selection([
                 ('invoice', 'Invoice'),
                 ('not_invoice', 'Not Invoice'),
                 ('tobeinvoice', 'To be Invoice'),
                 ], string = "Invoice", help = "is a invoiced task", compute='_compute_invoice', store=True)
    kind_task_id = fields.Many2one('ccorp.project.oerp.work.type','Type of task',required=True)

    @api.one
    @api.depends("ticket_ids")
    def _compute_invoice(self):
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

class account_analitic(models.Model):

    _inherit = 'account.analytic.account'
    
    invoice_type_id= fields.One2many('invoice.type', 'contract_type_id', string='Invoice Type', required=True)