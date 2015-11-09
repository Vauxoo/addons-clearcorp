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

class account_analytic_prepaid_hours (models.Model):
    _name = 'account.analytic.prepaid_hours'
    
    name  = fields.Char('Name', required=True)
    quatity = fields.Float('Quantity', required=True)
    analitic_account_id  = fields.Many2one('account.analytic.account', string='Analytic Account')
    active = fields.Boolean('Active', default = True)
    
class account_analytic_prepaid_hours_assigment (models.Model):
    _name = 'account.analytic.quantity_max_group.assigment'
    
    date = fields.Datetime('Date:')
    quatity = fields.Float('Quantity', required=True)
    group_id = fields.Many2one('account.analytic.quantity_max_group')
    
class account_analytic_quantity_max_group_approved_values (models.Model):
    _name = 'account.analytic.quantity_max_group_approved_line'
    
   
    group_id = fields.Many2one('account.analytic.quantity_max_group')
    prepay_hours = fields.Float('Prepay hours')
    expent_hours= fields.Float('Expent hours')
    remaining_hours= fields.Float('Remaining hours')
    tobe_approve= fields.Float('To be approve hours')
    requested_hours= fields.Float('Feature hours')
    extra_hours= fields.Float('Extra hours')
    extra_amount= fields.Float('Extra amount')
    
class account_analytic_quantity_max_group_approval_line (models.Model):
    _name = 'account.analytic.quantity_max_group_approval'
    
    prepaid_hours_id = fields.Many2one('account.analytic.quantity_max_group')
    approval_id = fields.Many2one('account.analytic.quantity_group_approved')
    work_type_id = fields.Many2one('ccorp.project.oerp.work.type')
    quantity = fields.Float('Quantity prepaid')
    quantity = fields.Float('Quantity extra')
     
     
class account_analytic_quantity_max_group_approval(models.Model):
    _name = 'account.analytic.quantity_group_approved'
    
    ticket_id = fields.Many2one('project.issue', string='Ticket')
    user_id = fields.Many2one('res.user', string='User')
    date= fields.Date('Date')
    state = fields.Selection([('2b_approved', 'To approved'),('approved', 'Approved'),('rejected', 'Rejected')], string='State', default='draft')

class issue(models.Model):
    
    _inherit = 'project.issue'
    
    group_approved= fields.Many2many('account.analytic.quantity_group_approved')
     
    
    