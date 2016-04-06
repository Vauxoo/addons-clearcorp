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

from openerp.osv import osv,fields, orm
from openerp.tools.translate import _
import math
from datetime import datetime
import pytz
from openerp import SUPERUSER_ID

class ProjectIssue(osv.Model):
    _inherit = 'project.issue'
    
    def name_get(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name', 'issue_number'], context)

        for record in reads:
            name = record['name']
            if record['issue_number']:
                name = '[' + record['issue_number'] + ']' + ' ' + name
            res.append((record['id'], name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        res = super(ProjectIssue, self).name_search(cr, uid, name, args = args, operator = 'ilike', context = context)
        ids=self.search(cr, uid, [('issue_number', operator, name)] + args,
                              limit=limit, context=context)
        res = list(set(res + self.name_get(cr, uid, ids, context)))
        return res
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result={}
        domain=[]
        result = super(ProjectIssue, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            domain.append(('picking_type_id.code','=','outgoing'))
            domain.append(('state','=','done'))
            domain.append(('invoice_state','=','none'))
            domain.append(('delivery_note_id','!=','False'))
            domain.append(('partner_id', '=',partner_id))
            partner_obj=self.pool.get('res.partner')
            partner_ids=partner_obj.search(cr, uid,[('parent_id','=',partner_id),('partner_type','=','branch')])
            result.update({'domain':{'backorder_ids':domain}})
            if not partner_ids:
                result.update({'value':{'have_branch': False,'branch_id':False,'analytic_account_id':False}})
            if partner_ids:
                result.update({'value':{'have_branch': True,'branch_id':False,'analytic_account_id':False}})
  
        return result
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id,context={}):
        data = {}
        if prodlot_id:
            prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context)
            data.update({'product_id': prodlot.product_id.id})
        return {'value': data}
    
    def onchange_product_id(self, cr, uid, ids, product_id,partner_id,branch_id,context={}):
        data = {}
        domain=[]
        employee_ids=[]
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context)
            employee_obj = self.pool.get('hr.employee')
            if product.category_ids:
                for categ_prod in product.category_ids:
                    for employee in categ_prod.employee_ids:
                        employee_ids.append(employee.id)
                if employee_ids:
                    domain.append(('id', 'in',employee_ids))
            data.update({'categ_id': product.categ_id.id,'prodlot_id': False})
        return {'value': data,'domain':{'employee_id':domain}}
    
    def onchange_categ_id(self, cr, uid,ids,categ_id,context={}):
            data={}
            if categ_id:
                    data.update({'product_id': False,'prodlot_id': False})
            return {'value': data}
    
    def onchange_branch_id(self, cr, uid, ids, branch_id,context={}):
        result = {}
        domain=[]
        if branch_id:
            domain.append(('picking_type_id.code','=','outgoing'))
            domain.append(('state','=','done'))
            domain.append(('invoice_state','=','none'))
            domain.append(('delivery_note_id','!=','False'))
            domain.append(('partner_id', '=',branch_id))
            branch = self.pool.get('res.partner').browse(cr, uid, branch_id, context)
            result.update({'value':{'partner_id': branch.parent_id.id}})
            result.update({'domain':{'backorder_ids':domain}})
        return result
    
    def create(self, cr, uid, vals, context=None):
        employee_obj=self.pool.get('hr.employee')
        issue_number = self.pool.get('ir.sequence').get(cr, uid, 'project.issue', context=context) or '/'
        vals['issue_number'] = issue_number
        if 'employee_id' in vals:
            if vals.get('employee_id'):
                employee=employee_obj.browse(cr,uid, vals.get('employee_id'),context=context)[0]
                if employee.user_id:
                    vals['user_id'] = employee.user_id.id
                else:
                    raise osv.except_osv(_('Error!'), _('The employee asigned no have a user in the system'))
            else:
                vals['user_id'] = False
        result = super(ProjectIssue, self).create(cr, uid, vals, context=context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
         employee_obj=self.pool.get('hr.employee')
         type_obj=self.pool.get('project.task.type')
         if 'employee_id' in vals:
            if vals.get('employee_id'):
                employee=employee_obj.browse(cr,uid, vals.get('employee_id'),context=context)[0]
                if employee.user_id:
                    vals['user_id'] = employee.user_id.id
                else:
                    raise osv.except_osv(_('Error!'), _('The employee asigned no have a user in the system'))
            else:
                vals['user_id'] = False
         if 'stage_id' in vals:
             if vals.get('stage_id'):
                 type=type_obj.browse(cr,uid, vals.get('stage_id'),context=context)[0]
                 issue=self.browse(cr,uid,ids,context)
                 if type.closed==False and issue.stage_id.closed==True:
                     raise osv.except_osv(_('Error!'), _('The issue is closed, can not change the state'))
         res = super(ProjectIssue, self).write(cr, uid, ids, vals, context=context)
         return res
     
    def _check_issue_type(self, cr, uid, ids, context={}):
        for issue_obj in self.browse(cr, uid, ids, context=context):
            if issue_obj.issue_type!="remote support":
                for timesheet_obj in issue_obj.timesheet_ids:
                    if not timesheet_obj.ticket_number:
                        return False
                    else:
                        return True
        return True
    
    def get_stock_picking(self, cr, uid,ids,field_name,arg,context=None):
         picking_obj=self.pool.get('stock.picking')
         picking_ids=[]
         domain=[] 
         res={}
         domain.append(('picking_type_id.code','=','outgoing'))
         domain.append(('state','=','done'))
         domain.append(('invoice_state','=','none'))
         domain.append(('delivery_note_id','!=','False'))
         for issue in self.browse(cr, uid, ids, context=context):
             if issue.branch_id:
                domain.append(('partner_id','=',issue.branch_id.id))
             else:
                domain.append(('partner_id', '=', issue.partner_id.id))
             
             stock_picking_ids=picking_obj.search(cr, uid, domain)
             for stock_picking in picking_obj.browse(cr, uid, stock_picking_ids, context=context):
                 picking_ids.append(stock_picking.id)
             res[issue.id]=picking_ids
         return res
     
    _columns = {
                'issue_type': fields.selection([('remote support','Remote Support'),('site support','Site Visit'),('preventive check','Preventive Check'),
                                              ('workshop repair','Workshop Repair'),('installation','Installation'),('In Office','In Office')],
                                             required=True,string="Issue Type"),
                'issue_number': fields.char(string='Issue Number', select=True),
                'warranty': fields.selection([('seller','Seller'),('manufacturer','Manufacturer')],string="Warranty"),
                'init_onchange_call': fields.function(get_stock_picking, method=True, type='many2many', relation='stock.picking',string='Nothing Display', help='field at view init'),
                'backorder_ids': fields.one2many('stock.picking','issue_id',string="Backorders"),
                'origin_id':fields.many2one('project.issue.origin',string="Origin"),
                'partner_type':fields.related('partner_id','partner_type',relation='res.partner',string="Partner Type"),
                'categ_id':fields.many2one('product.category',required=True,string="Category Product"),
                'product_id':fields.many2one('product.product',string="Product"),
                'prodlot_id':fields.many2one('stock.production.lot',string="Serial Number"),
                'branch_id':fields.many2one('res.partner', string='Branch'),
                'employee_id': fields.many2one('hr.employee', 'Technical Staff Assigned'),
                'contact': fields.char(string="Reported by",required=True),
                'have_branch':fields.boolean(string="Have Branch"),
                'issue_related':fields.many2one('project.issue',string="Issue Related")
                }
    _constraints = [
        (_check_issue_type,'Must type the the ticket number, except in issue type Remote Support not is required',['issue_type','timesheet_ids']
         )]
    _defaults = {
        'date': fields.datetime.now,
    }
    _order = "create_date desc"
class ProjectIssueOrigin(osv.Model):
    _name = 'project.issue.origin'
     
    _columns = {
                 'name': fields.char(required=True,string="Name"),
                 'description': fields.text(string="Description")
                 }
 
class HrAnaliticTimeSheet(osv.Model):
    _inherit = 'hr.analytic.timesheet'
     
    def create(self, cr, uid, vals, context=None):
        employee_obj=self.pool.get('hr.employee')
        if vals.get('employee_id'):
            employee=employee_obj.browse(cr,uid, vals.get('employee_id'),context=context)[0]
            if employee.user_id:
                 vals['user_id'] = employee.user_id.id
            else:
                 raise osv.except_osv(_('Error!'), _('The employee asigned no have a user in the system'))
        result = super(HrAnaliticTimeSheet, self).create(cr, uid, vals, context=context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
         employee_obj=self.pool.get('hr.employee')
         if vals.get('employee_id'):
            employee=employee_obj.browse(cr,uid, vals.get('employee_id'),context=context)[0]
            if employee.user_id:
                 vals['user_id'] = employee.user_id.id
            else:
                raise osv.except_osv(_('Error!'), _('The employee asigned no have a user in the system'))
         res = super(HrAnaliticTimeSheet, self).write(cr, uid, ids, vals, context=context)
         return res
     
    def _check_future_timesheets(self, cr, uid, ids, context={}):
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, SUPERUSER_ID, uid)
        utc = pytz.timezone('UTC')
        tz = pytz.timezone(user.partner_id.tz) or pytz.utc
        for timesheet_obj in self.browse(cr, uid, ids, context=context):
                hour_start = math.floor(timesheet_obj.start_time)
                min_start = round((timesheet_obj.start_time % 1) * 60)
                hour_end = math.floor(timesheet_obj.end_time)
                min_end = round((timesheet_obj.end_time % 1) * 60)
                datetime_start = tz.localize(datetime.strptime(timesheet_obj.date+' '+str(int(hour_start))+':'+str(int(min_start)),'%Y-%m-%d %H:%M'), is_dst=False)
                datetime_end = tz.localize(datetime.strptime(timesheet_obj.date+' '+str(int(hour_end))+':'+str(int(min_end)),'%Y-%m-%d %H:%M'), is_dst=False)
                datetime_start = datetime_start.astimezone(utc)
                datetime_end = datetime_end.astimezone(utc)
                if datetime_start>datetime.now(utc) or datetime_end>datetime.now(utc):
                    return False
        return True
     
    def _check_start_time(self, cr, uid, ids, context={}):
        hour=0.0
        min=0.0
        for timesheet_obj in self.browse(cr, uid, ids, context=context):
            if timesheet_obj.start_time:
                hour = math.floor(timesheet_obj.start_time)
                min = round((timesheet_obj.start_time % 1) * 60)
            if (hour not in range(0,24) or min not in range(0,60)):
                return False
        return True
     
    def _check_end_time(self, cr, uid, ids, context={}):
        hour=0.0
        min=0.0
        for timesheet_obj in self.browse(cr, uid, ids, context=context):
            if timesheet_obj.end_time:
                hour = math.floor(timesheet_obj.end_time)
                min = round((timesheet_obj.end_time % 1) * 60)
            if (hour not in range(0,24) or min not in range(0,60)):
                if (hour==24 and min==00):
                    return True
                else:
                    return False
        return True
    
    def _check_ticket_number(self, cr, uid, ids, context={}):
        for timesheet_obj in self.browse(cr, uid, ids, context=context):
            if timesheet_obj.issue_id:
                if timesheet_obj.issue_id.issue_type!="remote support":
                    if not timesheet_obj.ticket_number:
                        return False
                    else:
                        return True
        return True
     
    def onchange_start_time(self, cr, uid, ids, start_time, end_time):
        duration=end_time-start_time
        return {'value': {'unit_amount': duration,'amount_unit_calculate':duration}}
     
    def onchange_end_time(self, cr, uid, ids, start_time, end_time):
        duration=end_time-start_time
        return {'value': {'unit_amount': duration,'amount_unit_calculate':duration}}
    
    def get_duration(self, cr, uid, ids, name, args, context=None):
        res = {}
        for timesheet in self.browse(cr, uid, ids, context=context):
            res[timesheet.id]=timesheet.end_time-timesheet.start_time
        return res
     
    _columns = {
                'ticket_number': fields.char(string="Ticket Number"),
                'start_time': fields.float(string="Start Time"),
                'end_time': fields.float(string="End Time"),
                'service_type': fields.selection([('expert','Expert'),('assistant','Assistant'),('basic','Basic')],string="Service Type"),
                'employee_id': fields.many2one('hr.employee', 'Technical Staff'),
                'amount_unit_calculate': fields.function(get_duration, method=True, store=True,type='float',string='Amount Unit'),
                'task_id': fields.many2one('project.task', 'Task Assigned'),
                'project_id':fields.related('task_id','project_id',type='many2one',relation='project.project',string='Project',readonly=True, store=True),
                }
     
    _constraints = [
        (_check_ticket_number,'Must type the the ticket number, except in issue type Report Support not is required',['ticket_number']
         ),
        (_check_start_time,'Format Start Time incorrect',['start_time']
         ),
         (_check_end_time,'Format End Time incorrect',['end_time']
         ),
         (_check_future_timesheets,'Date time is greater than now',['start_time','end_time','date'])]
    
    _defaults = {
          'service_type':'expert'
                }

    _sql_constraints = [('unique_ticket_number','UNIQUE(ticket_number)',
                         'Ticket number must be unique for every worklogs')]
class StockPicking(orm.Model):
     _inherit = 'stock.picking'
 
     _columns = {
          'issue_id': fields.many2one('project.issue')
     }
class ProductTemplate(orm.Model):
    _inherit = 'product.template'
    _name = 'product.template'
     
    def create(self, cr, uid, vals, context=None):
        product_obj=self.pool.get('product.product')
        new_product=super(ProductTemplate, self).create(cr, uid, vals, context=context)
         
        category_ids=vals.get('category_ids',False)
        alternative_product_ids = vals.get('alternative_product_ids', False)
        accessory_product_ids = vals.get('accessory_product_ids', False)
        if alternative_product_ids:
            for products in alternative_product_ids:
                for product in products[2]:
                    super(ProductTemplate, self).write(cr, uid,product, {
               'alternative_product_ids':  [(6,0,[new_product])] 
            }, context=context)
        if category_ids:
            for categories in category_ids:
                for category in categories[2]:
                    self.write(cr, uid,new_product, {
                'category_ids':  [(6,0,[category])] 
                }, context=context)
                     
        return new_product

    def write(self, cr, uid, ids, vals, context=None):
        product_obj=self.pool.get('product.product')
        res = super(ProductTemplate, self).write(cr, uid, ids, vals, context=context)
        alternative_product_ids = vals.get('alternative_product_ids', False)
        accessory_product_ids = vals.get('accessory_product_ids', False)
        if alternative_product_ids:
            for products in alternative_product_ids:
                for product in products[2]:
                    super(ProductTemplate, self).write(cr, uid,product, {
               'alternative_product_ids':  [(6,0,ids)] 
            }, context=context)
        return res
     
    def onchange_supply_type(self, cr, uid, ids, supply_type, context=None):
         product_ids=[]
         domain=[]
         if supply_type:
             if supply_type=='equipment':
                 domain.append(('supply_type', 'in', ('supply','replacement')))
             elif supply_type=='supply':
                 domain.append(('supply_type', '=', 'equipment'))
             elif supply_type=='replacement':
                 domain.append(('supply_type', '=', 'equipment'))
                 
             product_template_ids=self.search(cr, uid,domain)
             
             product_ids=self.pool.get('product.product').search(cr, uid, [('product_tmpl_id','in',product_template_ids)])
        
         return{'domain':{'accessory_product_ids':[('id','in',product_ids)]}}


    def get_accessory_product(self, cr, uid,ids,field_name,arg,context=None ):
         product_obj=self.pool.get('product.product')
         product_ids=[]
         domain=[] 
         res={}
         for product in self.browse(cr, uid, ids, context=context):
             if product.supply_type:
                 if product.supply_type=='equipment':
                     domain.append(('product_tmpl_id.supply_type', 'in', ('supply','replacement')))
                 elif product.supply_type=='supply':
                     domain.append(('product_tmpl_id.supply_type', '=', 'equipment'))
                 elif product.supply_type=='replacement':
                     domain.append(('product_tmpl_id.supply_type', '=', 'equipment'))

             
                 accessory_product_ids=product_obj.search(cr, uid, domain)
                 for accessory_product in product_obj.browse(cr, uid, accessory_product_ids, context=context):
                     product_ids.append(accessory_product.id)
                 res[product.id]=product_ids   
         return res

    _columns = {
        'category_ids':fields.related('product_variant_ids', 'category_ids', relation='hr.employee.category', type='many2many', string='Employee Profile'),
        'init_onchange_call': fields.function(get_accessory_product, method=True, type='many2many', relation='product.product',string='Nothing Display', help='field at view init'),
        'supply_type':fields.selection([('equipment','Equipment'),('replacement','Replacement'),('supply','Supply'),
                                               ('input','Input'),('service','Service')],string="Supply Type"),
         }

class Product(orm.Model):
    _inherit = 'product.product'
    _name = 'product.product'
    
    def onchange_supply_type(self, cr, uid, ids, supply_type, context=None):
         product_ids=[]
         domain=[]
         if supply_type:
             if supply_type=='equipment':
                 domain.append(('supply_type', 'in', ('supply','replacement')))
             elif supply_type=='supply':
                 domain.append(('supply_type', '=', 'equipment'))
             elif supply_type=='replacement':
                 domain.append(('supply_type', '=', 'equipment'))
                 
             product_template_ids=self.search(cr, uid,domain)
             
             product_ids=self.pool.get('product.product').search(cr, uid, [('product_tmpl_id','in',product_template_ids)])
        
         return{'domain':{'accessory_product_ids':[('id','in',product_ids)]}}
    _columns = {
             'category_ids': fields.many2many('hr.employee.category', 'employee_product_category_rel', 'product_id', 'category_id', 'Employee Profile')
             }
class ProductCategory(orm.Model):
     _inherit = 'product.category'
     
     _columns = {
         'department_ids':fields.many2many('hr.department',string='Department'),
         'supply_type':fields.selection([('equipment','Equipment'),('replacement','Replacement'),('supply','Supply'),
                                               ('input','Input'),('service','Service')],string="Supply Type")
         }

class StockPickingType(orm.Model):
    _inherit = 'stock.picking.type'
    _columns = {
         'issue_required':fields.boolean(string='Issue Required',help="If this field has a check, the issue is required"),
         }

class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _compute_issue_required(self, cr, uid, context=None):
        context = context or {}
        if context.get('default_picking_type_id', False):
            pick_type = self.pool.get('stock.picking.type').browse(cr, uid, context['default_picking_type_id'], context=context)
            return pick_type.issue_required or False
        return False

    def get_domain_issue_id(self,cr,uid,ids,partner_id,context=None):
        if partner_id:
            issue_ids=self.pool.get('project.issue').search(cr,uid,['|',('branch_id','=',partner_id),('partner_id','=',partner_id),('is_closed','=',False)])
            return {'domain':{'issue_id':[('id','in',issue_ids)]},'value':{'issue_id':False}}
        else:
            return {'domain':{'issue_id':False},'value':{'issue_id':False}}
    def get_issue_required(self,cr,uid,ids,picking_type_id,context=None):
            picking_type_id=self.pool.get('stock.picking.type').browse(cr, uid, picking_type_id, context=context)
            return {'value':{'issue_required':picking_type_id.issue_required}}
    
    def get_issues_partner(self, cr, uid,ids,field_name,arg,context=None ):
        issue_obj=self.pool.get('project.issue')
        picking_ids=[]
        domain=[]
        res={}
        for picking in self.browse(cr, uid, ids, context=context):
            issue_ids=issue_obj.search(cr, uid, ['|',('branch_id','=',picking.partner_id.id),('partner_id','=',picking.partner_id.id)])
            for issue in issue_obj.browse(cr, uid, issue_ids, context=context):
                if issue.is_closed==False:
                    picking_ids.append(issue.id)
        res[picking.id]=picking_ids
        return res
    
    _columns = {
         'init_onchange_call': fields.function(get_issues_partner, method=True, type='many2many', relation='project.issue',string='Nothing Display', help='field at view init'),
         'issue_id':fields.many2one('project.issue',string="Issue"),
         'issue_required':fields.boolean(string='Issue Required'),
              }
    _defaults = {
          'issue_required':_compute_issue_required
                }
class SaleOrder(orm.Model):
    _inherit = 'sale.order'
    
    def onchange_project_project_id(self, cr, uid, ids, project_project_id,context={}):
        data = {}
        if project_project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_project_id, context)
            data.update({'project_id': project.analytic_account_id.id})
        return {'value': data}
    
    def write(self,cr, uid, ids, vals, context=None):
        if not vals.has_key('project_id') and vals.has_key('project_project_id') and vals.get('project_project_id')!=False:
            project_obj=self.pool.get('project.project')
            project_ids=project_obj.search(cr, uid,[('id','=',vals.get('project_project_id'))])
            project=project_obj.browse(cr, uid, project_ids[0], context=context)
            vals.update({'project_id': project.analytic_account_id.id})
        return super(SaleOrder, self).write(cr, uid, ids, vals, context=context)

    def create(self,cr, uid, vals, context=None):
        if not vals.has_key('project_id') and vals.has_key('project_project_id') and vals.get('project_project_id')!=False:
            project_obj=self.pool.get('project.project')
            project_ids=project_obj.search(cr, uid,[('id','=',vals.get('project_project_id'))])
            project=project_obj.browse(cr, uid, project_ids[0], context=context)
            vals.update({'project_id': project.analytic_account_id.id})
        return super(SaleOrder, self).create(cr, uid, vals, context=context)

    _columns = {
         'project_project_id':fields.many2one('project.project',string="Project")
              }
class ResUsers(orm.Model):
    _inherit = 'res.users'
    def _get_user_from_employee(self, cr, uid, ids, name, arg, context=None):
        """Computes the fields.function employee_id"""
        result = {}
        for user in self.read(cr, uid, ids, ['id', 'name'], context=context):
            res_search = self.pool.get('hr.employee').search(cr, uid,
                    [('user_id', '=', user['id'])], context=context)
            if len(res_search) == 1:
                result[user['id']] = res_search[0]
            elif len(res_search) > 1:
                list_employee_names = u''
                for employee in self.pool.get('hr.employee').read(cr, uid, res_search, ['name'], context=context):
                    list_employee_names += employee['name'] + u', '
                raise osv.except_osv(_('Error :'), _("You have several employees (%s) pointing to the same user '%s'")% (list_employee_names, user['name']))
            else:
                result[user['id']] = False
        return result
    def _get_employee_from_user(self, cr, uid, ids, context=None):
        users_of_updated_employees = []
        for employee in self.read(cr, uid, ids, ['name', 'user_id'], context=context):
            if employee['user_id']:
                users_of_updated_employees.append(employee['user_id'][0])
        res= self.pool.get('res.users').search(cr, uid, ['|', '|', ('employee_id', 'in', ids), ('employee_id', '=', False), ('id', 'in', users_of_updated_employees)], context=context)
        return res
    
    _columns = {
        'employee_id': fields.function(_get_user_from_employee, string='Employee',
            type='many2one', relation='hr.employee', store={
                'hr.employee': (_get_employee_from_user, ['user_id'], 10),
            }, help="Related employee. This field is automatically computed from the 'User' field on the 'Employees' form in the Human Resources menu.")
    }
    
    