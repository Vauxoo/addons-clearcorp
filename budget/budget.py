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

from operator import itemgetter
from tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging
import netsvc

from osv import fields, osv

##
#PLAN
## 
class budget_plan(osv.osv):
    _name = 'budget.plan'
    _description = 'Plan'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled'),
    ]
    _columns ={
        'name': fields.char('Name', size=64, required=True),
        'year_id': fields.many2one('budget.year','Year',required=True),
        'state':fields.selection(STATE_SELECTION, 'State', readonly=True, 
        help="The state of the bugdet. A budget that is still under planning is in a 'Draft' state. Then the plan has to be confirmed by the user in order to be approved, the state switch to 'Confirmed'. Then the manager must confirm the budget plan to change the state to 'Approved'. If a plan will not be approved it must be cancelled.", select=True),
        'plan_lines':fields.one2many('budget.plan.line','plan_id','Lines'),
        }
    
    _defaults ={
        'state': 'draft'
        }
    
    _sql_constraints = [
        ('name', 'unique(name)','The name must be unique !'),
        ]
    
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def check_no_orphan_accounts(self, cr, uid, ids, context=None):
        #Verifies that every active budget account is included in the plan 
        for plan_id in ids:
            query = 'SELECT BA.id, BA.composite_code, BA.name FROM '\
            'budget_account BA '\
            'WHERE BA.account_type = \'%(account_type)s\' ' \
            'AND active = true '\
            'EXCEPT '\
            'SELECT BA.id, BA.composite_code , BA.name FROM '\
            'budget_account BA INNER JOIN budget_plan_line BPL ON BA.ID = BPL.account_id '\
            'INNER JOIN budget_plan BP ON BPL.plan_id = BP.id '\
            'WHERE BP.id = %(plan_id)d' % {'plan_id':plan_id, 'account_type':'budget'}
            cr.execute(query)
        result = cr.fetchall()
        account_list = ''
        if result.__len__() > 0:
            for line in result:
                account_list = account_list + '%s - %s \n'  % (line[1],line[2]) 
            raise osv.except_osv(_('Error!'), _('The following budget accounts are not listed in this plan: \n ' + account_list  ))
        return True
    
    def check_no_consolidated_orphans(self, cr, uid, ids, context=None):
        query = 'SELECT composite_code, name FROM budget_account '\
                'WHERE id IN( '\
                'SELECT id FROM budget_account '\
                'WHERE account_type = \'budget\' '\
                'EXCEPT '\
                'SELECT DISTINCT consol_child_id '\
                'FROM budget_account_consol_rel) '
        cr.execute(query)        
        result = cr.fetchall()
        account_list = ''
        if result.__len__() > 0:
            for line in result:
                account_list = account_list + '%s - %s \n'  % (line[0],line[1]) 
            raise osv.except_osv(_('Error!'), _('The following budget accounts are not consolidated children of any consolidation view: \n ' + account_list  ))
        return True 
    
    def action_confirm(self, cr, uid, ids, context=None):
        if self.check_no_orphan_accounts(cr, uid, ids, context=context):
            if self.check_no_consolidated_orphans(cr, uid, ids, context=context):
                self.write(cr, uid, ids, {'state': 'confirmed'})
                return True     

    def action_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})
        return True
    
    def action_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'closed'})
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        for plan in self.browse(cr, uid,ids, context=context):
            if plan.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot delete an approved or closed plan'))
        return super(budget_plan, self).unlink(cr, uid, ids, context=context)
 
##
#PLAN LINE
## 
  
    def bulk_line_create(self, cr, uid, ids, context=None):            
        line_obj = self.pool.get('budget.plan.line')
        account_obj = self.pool.get('budget.account')
        for plan in self.browse(cr, uid, ids, context=context):
            current_lines = len(plan.plan_lines)
            if current_lines > 0:
                raise osv.except_osv(_('Error!'), _('This plan already contains plan lines'))   
            year = plan.year_id           
            str_year = year.date_start[0:4]
            account_ids= account_obj.search(cr,uid,[('active','=','true'),('account_type','=','budget')])
            for account in account_obj.browse(cr,uid,account_ids):
                line_name = 'LP '+ plan.name +' ' + str_year + ' - ' +account.composite_code
                line_account_id = account.id
                line_plan_id = plan.id
                line_obj.create(cr,uid,{
                                        'name':line_name,
                                        'account_id':line_account_id,
                                        'plan_id':line_plan_id,                                                                              
                                        }) 
        
class budget_plan_line(osv.osv):
    _name = 'budget.plan.line'
    _description = 'Plan line'
    
    def get_execution_percentage(self, cr, uid, ids, field_name, args, context=None):
        test = {}
        for id in ids:
            test[id]= 0.0 
        return test
   
    def get_available_budget(self, cr, uid, ids, field_name, args, context=None):
        test = {}
        for id in ids:
            test[id]= 0.0 
        return test
    
    def get_available_cash(self, cr, uid, ids, field_name, args, context=None):
        test = {}
        for id in ids:
            test[id]= 0.0 
        return test
    
    def _check_unused_account(self, cr, uid, ids, context=None):
        #checks that the selected budget account is not associated to another plan line
        for line in self.read(cr,uid,ids,['account_id','plan_id']):
            cr.execute('SELECT count(1) '\
                        'FROM '+self._table+' '\
                        'WHERE account_id = %s '\
                        'AND id != %s'\
                        'AND plan_id = %s',(line['account_id'][0],line['id'],line['plan_id'][0]))
            
            if cr.fetchone()[0] > 0:        
                raise osv.except_osv(_('Error!'), _('There is already a plan line using this budget account'))
        return True
        
    
    _columns ={
        'name': fields.char('Name', size=64, required=True),
        'account_id': fields.many2one('budget.account','Budget account',required=True),
        'plan_id': fields.many2one('budget.plan','Plan',required=True),
        'assigned_ammount': fields.float('Assigned ammount', required=True),
        'execution_percentage': fields.function(get_execution_percentage, string='Execution Percentage', type="float", store=True),
        'available_budget': fields.function(get_available_budget, string='Available budget', type="float", store=True),
        'available_cash': fields.function(get_available_cash, string='Available Cash', type="float", store=True),
        'sponsor_id':fields.many2one('res.partner','Sponsor'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        }
    
    _defaults = {
        'assigned_ammount': 0.0,         
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
     
    _constraints = [
        (_check_unused_account, 'Error!\nThe budget account is related to another plan line.', ['account_id','plan_id']),
    ]
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'The name of the line must be unique per company!'),
    ]
    
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid,ids, context=context):
            if line.plan_id.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot delete a line from an approved or closed plan'))
        return super(budget_plan_line, self).unlink(cr, uid, ids, context=context)
    

class budget_account(osv.osv):
    _name = 'budget.account'
    _description = 'Budget Account'
    _order = "composite_code"
    #_parent_order = "composite_code"
    #_parent_store = True    
    _order = 'composite_code'

    def check_cycle(self, cr, uid, ids, context=None):
        """ climbs the ``self._table.parent_id`` chains for 100 levels or
        until it can't find any more parent(s)

        Returns true if it runs out of parents (no cycle), false if
        it can recurse 100 times without ending all chains
        """
        level = 100
        while len(ids):
            cr.execute('SELECT DISTINCT parent_id '\
                    'FROM '+self._table+' '\
                    'WHERE id IN %s '\
                    'AND parent_id IS NOT NULL',(tuple(ids),))
            ids = map(itemgetter(0), cr.fetchall())
            if not level:
                return False
            level -= 1
        return True
    
    def check_max_institutional_parents(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        view_type = ('institutional',)
        for account in self.browse(cr, uid, ids, context=context):
            cr.execute('SELECT count(1) '\
                    'FROM '+self._table+' '\
                    'WHERE parent_id IS NULL '\
                    'AND account_type =%s', view_type)
            if cr.fetchone()[0] >= 2:
                return False
        return True
                      
    def onchange_account_parent(self, cr, uid, ids, account_type, context=None):
        search_domain = [('account_type', '=', 'undefined')]
        if account_type:
            parent_type = 'view' #default
            search_domain = [('account_type', '=', 'view')]
            if account_type == 'consolidation' or account_type == 'institutional':
                search_domain = [('account_type', '=', 'institutional')]            
        return {'domain': {'parent_id': search_domain} }
    
    def get_composite_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            code = ''
            acc_id = account.id
            temp_account = account
            while temp_account:
                code =  temp_account.code + '.' + code
                temp_account = temp_account.parent_id
            res[acc_id] = code[:-1]
        return res
        
    _columns ={
        'active':fields.boolean('Active'),
        'code': fields.char('Code', size=64, required=True, select=1),
        'name': fields.char('Name', size=256,),
        'composite_code': fields.function(get_composite_code, string='Full Code', type="char", store=True),
        'account_type': fields.selection([
            ('budget', 'Budget Entry'),# CP
            ('view', 'Budget View'), # VP
            ('consolidation', 'Consolidation Entry'), # PC
            ('institutional', 'Institutional View'), # VI
        ], 'Internal Type', required=True, help="The 'Internal Type' is used for features available on "\
            "different types of accounts: view can not have journal items, consolidation are accounts that "\
            "can have children accounts for consolidations and can only have institutional views as parent, "\
            "institutional can have only consolidation childs"),
        'parent_id': fields.many2one('budget.account','Parent'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'child_consol_ids': fields.many2many('budget.account', 'budget_account_consol_rel', 'parent_id' ,'consol_child_id' , 'Consolidated Children'),
        }
    
    _defaults = {
        'account_type': 'budget',
        'active': True,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
    }
    
    _check_recursion = check_cycle
    _check_inst_parents = check_max_institutional_parents
    
    _constraints = [
        (_check_recursion, 'Error!\nYou cannot create recursive account templates.', ['parent_id']),
        (_check_inst_parents, 'Error!\nYou can create only 1 top level institutional view.', ['parent_id']),
    ]
    _sql_constraints =[
        ('check_unique_budget_account','unique (parent_id,code,company_id)','The code is defined for another account with the same parent' )
    ]
      
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        return super(budget_account, self).copy(cr, uid, id, default, context)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []    
        if not len(ids):
            return res
            
        for r in self.read(cr, uid, ids, ['composite_code','name'], context):
            rec_name = '[%s] %s' % (r['composite_code'], r['name']) 
            res.append( (r['id'],rec_name) )
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []

        if name and operator in ('=', 'ilike', '=ilike', 'like'):
            """We need all the partners that match with the ref or name (or a part of them)"""
            ids = self.search(cr, uid, ['|',('composite_code', 'ilike', name),('name','ilike',name)] + args, limit=limit, context=context)
            if ids and len(ids) > 0:
                return self.name_get(cr, uid, ids, context)
        return super(budget_account,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
 
    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            #we may not know the level of the parent at the time of computation, so we
            # can't simply do res[account.id] = account.parent_id.level + 1
            level = 0
            parent = account.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            res[account.id] = level
        return res

##
#YEAR
## 
class budget_year(osv.osv):
    _name = "budget.year"
    _description = "Budget Year"
    _columns = {
        'name': fields.char('Budget Year', size=64, required=True),
        'code': fields.char('Code', size=6, required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_stop': fields.date('End Date', required=True),
        'period_ids': fields.one2many('budget.period', 'budgetyear_id', 'Periods'),
        'state': fields.selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
    _order = "date_start, id"


    def _check_duration(self, cr, uid, ids, context=None):
        obj_fy = self.browse(cr, uid, ids[0], context=context)
        if obj_fy.date_stop < obj_fy.date_start:
            return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe start date of a Budget year must precede its end date.', ['date_start','date_stop'])
    ]
    def create_period3(self, cr, uid, ids, context=None):
        return self.create_period(cr, uid, ids, context, 3)

    def create_period(self, cr, uid, ids, context=None, interval=1):
        period_obj = self.pool.get('budget.period')
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')

            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)

                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create(cr, uid, {
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'budgetyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    def find(self, cr, uid, dt=None, exception=True, context=None):
        res = self.finds(cr, uid, dt, exception, context=context)
        return res and res[0] or False

    def finds(self, cr, uid, dt=None, exception=True, context=None):
        if context is None: context = {}
        if not dt:
            dt = fields.date.context_today(self,cr,uid,context=context)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if context.get('company_id', False):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        args.append(('company_id', '=', company_id))
        ids = self.search(cr, uid, args, context=context)
        if not ids:
            if exception:
                raise osv.except_osv(_('Error!'), _('There is no budget year defined for this date.\nPlease create one from the configuration of the accounting menu.'))
            else:
                return []
        return ids

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('code', 'ilike', name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
##
#PERIOD
## 
class budget_period(osv.osv):
    _name = "budget.period"
    _description = "Budget period"
    _columns = {
        'name': fields.char('Period Name', size=64, required=True),
        'code': fields.char('Code', size=12),
        'date_start': fields.date('Start of Period', required=True, states={'done':[('readonly',True)]}),
        'date_stop': fields.date('End of Period', required=True, states={'done':[('readonly',True)]}),
        'budgetyear_id': fields.many2one('budget.year', 'Budget Year', required=True, states={'done':[('readonly',True)]}, select=True),
        'state': fields.selection([('draft','Open'), ('done','Closed')], 'Status', readonly=True,
                                  help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.'),
        'company_id': fields.related('budgetyear_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True)
    }
    _defaults = {
        'state': 'draft',
    }
    _order = "date_start"
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
    ]

    def _check_duration(self,cr,uid,ids,context=None):
        obj_period = self.browse(cr, uid, ids[0], context=context)
        if obj_period.date_stop < obj_period.date_start:
            return False
        return True

    def _check_year_limit(self,cr,uid,ids,context=None):
        for obj_period in self.browse(cr, uid, ids, context=context):
            if obj_period.budgetyear_id.date_stop < obj_period.date_stop or \
               obj_period.budgetyear_id.date_stop < obj_period.date_start or \
               obj_period.budgetyear_id.date_start > obj_period.date_start or \
               obj_period.budgetyear_id.date_start > obj_period.date_stop:
                return False

            pids = self.search(cr, uid, [('date_stop','>=',obj_period.date_start),('date_start','<=',obj_period.date_stop),('id','<>',obj_period.id)])
            for period in self.browse(cr, uid, pids):
                if period.budgetyear_id.company_id.id==obj_period.budgetyear_id.company_id.id:
                    return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe duration of the Period(s) is/are invalid.', ['date_stop']),
        (_check_year_limit, 'Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the budget year.', ['date_stop'])
    ]

    def next(self, cr, uid, period, step, context=None):
        ids = self.search(cr, uid, [('date_start','>',period.date_start)])
        if len(ids)>=step:
            return ids[step-1]
        return False
    
    def action_draft(self, cr, uid, ids, *args):
        mode = 'draft'
        cr.execute('update budget_period set state=%s where id in %s', (mode, tuple(ids),))
        return True

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('code','ilike',name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)]+ args, limit=limit)
        return self.name_get(cr, user, ids, context=context)


#class budget_plan(osv.osv):
    