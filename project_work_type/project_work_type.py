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

class WorkType(models.Model):
    
    _name = 'project.work.type'
    
    _order = 'sequence'
    
    name= fields.Char('name', size=128, required=True)
    product_id= fields.Many2one('product.product', string='Product', required='True')
    sequence= fields.Integer('Sequence', required=True)
    column_number= fields.Integer('Column Number', required=True)

class invoice_type (models.Model):
    _name = 'invoice.type'
    
    name= fields.Many2one('project.work.type',required='True')
    product_price = fields.Boolean('Use product price')
    product_id = fields.Many2one('product.product')
    price= fields.Float('Price')
    contract_type_id = fields.Many2one('contract.type')
    
    @api.one
    @api.onchange("name")
    def onchange_name(self):
        self.product_id = self.name.product_id
        return True
   
class Task(models.Model):
    
    _inherit = 'project.task'

    work_type_id = fields.Many2one('project.work.type', 'Type of task', required=True)


class account_analitic(models.Model):

    _inherit = 'account.analytic.account'
    
    invoice_type_id= fields.One2many('invoice.type', 'contract_type_id', string='Invoice Type', required=True)
