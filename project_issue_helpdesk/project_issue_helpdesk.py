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
        result = super(ProjectIssue, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            partner_obj=self.pool.get('res.partner')
            partner_ids=partner_obj.search(cr, uid,[('parent_id','=',partner_id),('partner_type','=','branch')])
              
            if not partner_ids:
                 result.update({'have_branch': False})
                 result.update({'branch_id':False})
              
            if partner_ids:                    
                 result.update({'have_branch': True})
  
        return {'value': result}
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id,context={}):
        data = {}
        if prodlot_id:
            prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context)
            data.update({'product_id': prodlot.product_id.id})
        return {'value': data}
    
    def onchange_product_id(self, cr, uid, ids, product_id,context={}):
        data = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context)
            data.update({'categ_id': product.categ_id.id})
            data.update({'prodlot_id': False})
        return {'value': data}
    
    def onchange_categ_id(self, cr, uid,ids,categ_id,context={}):
            data={}
            if categ_id:
                    data.update({'product_id': False})
                    data.update({'prodlot_id': False})
                   
            return {'value': data}
    
    def onchange_branch_id(self, cr, uid, ids, branch_id,context={}):
        data = {}
        if branch_id:
            branch = self.pool.get('res.partner').browse(cr, uid, branch_id, context)
            data.update({'partner_id': branch.parent_id.id})
          
        return {'value': data}
    
    def create(self, cr, uid, vals, context=None):
        employee_obj=self.pool.get('hr.employee')
        issue_number = self.pool.get('ir.sequence').get(cr, uid, 'project.issue', context=context) or '/'
        vals['issue_number'] = issue_number
        if vals.get('employee_id'):
            employee=employee_obj.browse(cr,uid, vals.get('employee_id'),context=context)[0]
            if employee.user_id:
                 vals['user_id'] = employee.user_id.id
            else:
                 vals['user_id'] = False
        result = super(ProjectIssue, self).create(cr, uid, vals, context=context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
         employee_obj=self.pool.get('hr.employee')
         if vals.get('employee_id'):
            employee=employee_obj.browse(cr,uid, vals.get('employee_id'),context=context)[0]
            if employee.user_id:
                 vals['user_id'] = employee.user_id.id
            else:
                vals['user_id'] = False
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
    _columns = {
                'issue_type': fields.selection([('remote support','Remote Support'),('site support','Site Visit'),('preventive check','Preventive Check'),
                                              ('workshop repair','Workshop Repair'),('installation','Installation')],
                                             required=True,string="Issue Type"),
                'issue_number': fields.char(string='Issue Number', select=True),
                'warranty': fields.selection([('seller','Seller'),('manufacturer','Manufacturer')],string="Warranty"),                                 
                'backorder_ids': fields.one2many('stock.picking','issue_id',domain=[('picking_type_id.code','=','outgoing')],string="Backorders"),
                'origin_id':fields.many2one('project.issue.origin',string="Origin"),
                'partner_type':fields.related('partner_id','partner_type',relation='res.partner',string="Partner Type"),
                'categ_id':fields.many2one('product.category',required=True,string="Category Product"),
                'product_id':fields.many2one('product.product',string="Product"),
                'prodlot_id':fields.many2one('stock.production.lot',string="Serial Number"),
                'branch_id':fields.many2one('res.partner', type='many2one', string='Branch'),
                'employee_id': fields.many2one('hr.employee', 'Technical Staff Assigned'),
                'contact': fields.char(string="Reported by",required=True),
                'have_branch':fields.boolean(string="Have Branch")
                }
    _constraints = [
        (_check_issue_type,'Must type the the ticket number, except in issue type Remote Support not is required',['issue_type','timesheet_ids']
         )]
    _defaults = {
        'date': fields.datetime.now,
    }

class ProjectIssueOrigin(osv.Model):
    _name = 'project.issue.origin'
     
    _columns = {
                 'name': fields.char(required=True,string="Name"),
                 'description': fields.text(string="Description")
                 }
 
class HrAnaliticTimeSheet(osv.Model):
    _inherit = 'hr.analytic.timesheet'
     
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
            if timesheet_obj.issue_id.issue_type!="remote support":
                if not timesheet_obj.ticket_number:
                    return False
                else:
                    return True
        return True
    def _compute_duration(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for timesheet_obj in self.browse(cr, uid, ids, context=context):
                res[timesheet_obj.id] = timesheet_obj.end_time-timesheet_obj.start_time
        return res
     
    def onchange_start_time(self, cr, uid, ids, start_time, end_time):
        duration=end_time-start_time
        return {'value': {'unit_amount': duration}}
     
    def onchange_end_time(self, cr, uid, ids, start_time, end_time):
        duration=end_time-start_time
        return {'value': {'unit_amount': duration}}
     
    _columns = {
                'ticket_number': fields.char(string="Ticket Number"),
                'start_time': fields.float(required=True,string="Start Time"),
                'end_time': fields.float(required=True,string="End Time"),
                'service_type': fields.selection([('expert','Expert'),('assistant','Assistant')],required=True,string="Service Type"),                       
                #'unit_amount_temp':fields.function(_compute_duration, type='float', string='Quantify',store=True),
                'employee_id': fields.many2one('hr.employee', 'Technical Staff'),
                }
     
    _constraints = [
        (_check_ticket_number,'Must type the the ticket number, except in issue type Reporte Support not is required',['ticket_number']
         ),
        (_check_start_time,'Format Start Time incorrect',['start_time']
         ),
         (_check_end_time,'Format End Time incorrect',['end_time']
         )]
      
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
         
         alternative_product_ids = vals.get('alternative_product_ids', False)
         accessory_product_ids = vals.get('accessory_product_ids', False)
         if alternative_product_ids:
             for products in alternative_product_ids:
                 for product in products[2]:
                     super(ProductTemplate, self).write(cr, uid,product, {
                'alternative_product_ids':  [(6,0,[new_product])] 
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
        'init_onchange_call': fields.function(get_accessory_product, method=True, type='many2many', relation='product.product',string='Nothing Display', help='field at view init'),
        'supply_type':fields.selection([('equipment','Equipment'),('replacement','Replacement'),('supply','Supply'),
                                               ('input','Input')],string="Supply Type"),
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

class ProductCategory(orm.Model):
     _inherit = 'product.category'
     
     _columns = {
         'supply_type':fields.selection([('equipment','Equipment'),('replacement','Replacement'),('supply','Supply'),
                                               ('input','Input')],string="Supply Type")
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
            issue_ids=self.pool.get('project.issue').search(cr,uid,['|',('branch_id','=',partner_id),('partner_id','=',partner_id)])
            return {'domain':{'issue_id':[('id','in',issue_ids)]}}
        else:
            return {'domain':{'issue_id':False}}
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

class StockTransferDetail(osv.osv_memory):
    _inherit = 'stock.transfer_details'
    
    def do_enter_transfer_partner(self, cr, uid,ids, context=None):
        stock_move_obj=self.pool.get('stock.move')
        stock_picking_obj=self.pool.get('stock.picking')
        stock_picking_type_obj=self.pool.get('stock.picking.type')
        stock_pack_operation_obj=self.pool.get('stock.pack.operation')
        stock_move_ids=[]
        
        for transfer in self.browse(cr, uid, ids, context=context):
            location_dest_original=transfer.picking_id.location_dest_id.id
            partner_original=transfer.picking_id.partner_id.id
            picking_type_original=transfer.picking_id.picking_type_id.id
            if transfer.picking_id.issue_id.branch_id:
                location_dest_actual=transfer.picking_id.issue_id.branch_id.property_stock_customer.id
                partner_actual=transfer.picking_id.issue_id.branch_id.id
            elif transfer.picking_id.issue_id.partner_id:
                location_dest_actual=transfer.picking_id.issue_id.partner_id.property_stock_customer.id
                partner_actual=transfer.picking_id.issue_id.partner_id.id
            else:
                raise osv.except_osv(_('Warning!'), _('You can not transfer to a partner, if you have not selected an issue'))  
            
            picking_type_id=stock_picking_type_obj.search(cr, uid,[('code','=','outgoing'),('warehouse_id','=',transfer.picking_id.picking_type_id.warehouse_id.id)])
            for move in transfer.picking_id.move_lines:
                stock_move_obj.write(cr,uid, move.id,{'location_dest_id': location_dest_actual,'partner_id':partner_actual,'picking_type_id':picking_type_id[0]})
                stock_move_ids.append(move.id)
            stock_picking_obj.write(cr,uid, transfer.picking_id.id,{'location_dest_id': location_dest_actual,'partner_id':partner_actual,'picking_type_id':picking_type_id[0]})
            self.do_detailed_transfer(cr,uid,ids,context)
            for pack in transfer.picking_id.pack_operation_ids:
                stock_pack_operation_obj.write(cr,uid,pack.id,{'location_dest_id': location_dest_actual})
            move_ids=stock_move_obj.search(cr, uid,[('split_from','in',stock_move_ids)])
            
            for move in stock_move_obj.browse(cr, uid, move_ids, context=context):
                    stock_move_obj.write(cr,uid, move.id,{'state': 'draft'})
                    stock_move_obj.write(cr,uid, move.id,{'location_dest_id': location_dest_original,'partner_id':partner_original,'state': 'done','picking_type_id':picking_type_original})
                    pack_operation_ids=stock_pack_operation_obj.search(cr, uid,[('picking_id','=',move.picking_id.id)])
                    for pack in stock_pack_operation_obj.browse(cr, uid, pack_operation_ids, context=context):
                        stock_pack_operation_obj.write(cr,uid, pack.id,{'location_dest_id': location_dest_original})
            stock_picking_obj.write(cr,uid, transfer.picking_id.id,{'invoice_state': '2binvoiced','picking_type_id':picking_type_id[0]})

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
    