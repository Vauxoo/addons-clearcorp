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
from openerp.exceptions import Warning

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    task_id=fields.Many2one('project.task',string="Project Task")
class ProjectTask(models.Model):
    _inherit = 'project.task'
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','code',], context=context)
        res = []
        for record in reads:
            name = record['name']
            code=record['code']
            if code:
                name=code + ' '+ name
            res.append((record['id'], name))
        return res
    @api.v7
    def name_search(self,cr,uid,name,args=None, operator='ilike',context=None, limit=100):
        res = super(ProjectTask, self).name_search(cr,uid,name, args = args, operator = 'ilike')
        ids=self.search(cr,uid,[('code', operator, name)] + args,limit=limit, context=context)
        ids2=self.search(cr,uid,[('project_id.code', operator, name)] + args,limit=limit, context=context)
        ids3=self.search(cr,uid,[('project_id.analytic_account_id.code', operator, name)] + args,limit=limit, context=context)
        res = list(set(res + self.name_get(cr, uid, ids, context=context)+self.name_get(cr, uid, ids2, context=context)+self.name_get(cr, uid, ids3, context=context)))
        return res
    def create(self, cr, uid, vals, context=None):
        code = self.pool.get('ir.sequence').get(cr, uid, 'project.task', context=context) or '/'
        vals['code'] = code
        result = super(ProjectTask, self).create(cr, uid, vals, context=context)
        return result
    @api.v7
    def write(self, cr, uid, ids, vals, context=None):
        tasks=self.browse(cr,uid,ids)
        if vals.get('stage_id'):
            type_obj=self.pool.get('project.task.type')
            type_ids=type_obj.search(cr, uid,[('id', '=', vals.get('stage_id'))])
            types=type_obj.browse(cr, uid,type_ids)
            for type in types:
                if type.closed==True:
                    for task in tasks:
                        for expense_line in task.expense_line_ids:
                            if not expense_line.expense_id.state in ['done','pain']:
                                raise Warning(_('Pending change status to done or paid of expense: %s' % expense_line.expense_id.name))
        return super(ProjectTask, self).write(cr, uid, ids, vals, context)
    @api.depends('project_id')
    @api.one
    def get_account_id(self):
        if self.project_id:
            if self.project_id.analytic_account_id:
                self.analytic_account_id=self.project_id.analytic_account_id
            else:
                self.analytic_account_id=False
    
    @api.onchange('categ_id')
    def get_product(self):
        if self.categ_id:
            products=self.env['product.product'].search([('categ_id','=',self.categ_id.id)])
            if not products:
                self.product_id=False
        else:
            self.product_id=False
            
    purchase_orde_line=fields.One2many('purchase.order.line','task_id')
    expense_line_ids=fields.One2many('hr.expense.line','task_id')
    account_invoice_line_ids=fields.One2many('account.invoice.line','task_id')
    timesheet_ids=fields.One2many('hr.analytic.timesheet','task_id')
    backorder_ids= fields.One2many('stock.picking','task_id')
    analytic_account_id = fields.Many2one('account.analytic.account',compute="get_account_id",string='Analytic Account',store=True)
    is_closed = fields.Boolean(string='Is Closed',related='stage_id.closed',store=True)
    categ_id=fields.Many2one('product.category',string="Category Product")
    product_id=fields.Many2one('product.product',string="Product")
    code = fields.Char(string='Reference')

class HRExpenseLine(models.Model):
    _inherit = 'hr.expense.line'
    @api.onchange('task_id')
    def get_account_task(self):
        if self.task_id:
            if self.task_id.analytic_account_id:
                self.analytic_account=self.task_id.analytic_account_id
            else:
                self.analytic_account=False
        else:
            self.analytic_account=False
    task_id=fields.Many2one('project.task',string="Project Task")
    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    task_id=fields.Many2one('project.task',string="Project Task")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.onchange('task_id')
    def get_account_task(self):
        if self.task_id:
            if self.task_id.analytic_account_id:
                self.account_analytic_id=self.task_id.analytic_account_id
            else:
                self.account_analytic_id=False
        else:
            self.account_analytic_id=False
            
    task_id=fields.Many2one('project.task','Project Task')