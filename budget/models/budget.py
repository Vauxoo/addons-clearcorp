# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from operator import itemgetter
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging
import openerp.netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, orm, osv

######################################################

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
    
    def _check_duration(self, cr, uid, ids, context=None):
        selected_plans = self.browse(cr, uid, ids, context=context)
        all_plan_ids = self.search(cr, uid, [], context=context)
        plans = self.browse(cr, uid, all_plan_ids, context=context)
        
        for selected_plan in selected_plans:
            if selected_plan.date_stop <= selected_plan.date_start:
                return False
        return True
    
    def _check_start_overlapping(self, cr, uid, ids, context=None):
        selected_plans = self.browse(cr, uid, ids, context=context)
        all_plan_ids = self.search(cr, uid, [], context=context)
        plans = self.browse(cr, uid, all_plan_ids, context=context)
        
        for selected_plan in selected_plans:
            for plan in plans:
                if selected_plan.id != plan.id and selected_plan.date_start >= plan.date_start and selected_plan.date_start <= plan.date_stop: ##Start date overlapped
                    return False 
        return True
    
    def _check_stop_overlapping(self, cr, uid, ids, context=None):
        selected_plans = self.browse(cr, uid, ids, context=context)
        all_plan_ids = self.search(cr, uid, [], context=context)
        plans = self.browse(cr, uid, all_plan_ids, context=context)
        
        for selected_plan in selected_plans:
            for plan in plans: 
                if selected_plan.id != plan.id and selected_plan.date_stop >= plan.date_start and selected_plan.date_stop <= plan.date_stop: ##stop date overlapped
                    return False
        return True

    _columns ={
        'name': fields.char('Name', size=64, required=True, states={'draft':[('readonly',False)]}),
        'date_start': fields.date('Start Date', required=True,states={'draft':[('readonly',False)]}),
        'date_stop': fields.date('End Date', required=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection(STATE_SELECTION, 'State', readonly=True, 
        help="The state of the budget. A budget that is still under planning is in a 'Draft' state. Then the plan has to be confirmed by the user in order to be approved, the state switch to 'Confirmed'. Then the manager must confirm the budget plan to change the state to 'Approved'. If a plan will not be approved it must be cancelled.", select=True),
        'program_ids':fields.one2many('budget.program','plan_id','Programs'),
        }
    
    _defaults ={
        'state': 'draft'
        }
    
    _constraints = [
        (_check_duration, 'Error!\nThe start date of the plan must precede its end date', ['date_start','date_stop']),
        (_check_start_overlapping, 'Error!\nThe start date of the plan must not overlap with another plan', ['date_start']),
        (_check_stop_overlapping, 'Error!\nThe stop date of the plan must not overlap with another plan', ['date_stop'])
    ]
    _sql_constraints = [
        ('name', 'unique(name)','The name must be unique !'),
        ]
    
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def check_programs(self, cr, uid, ids, context=None):
        for plan in self.browse(cr, uid, ids,context=context):
            if plan.program_ids.__len__() == 0:
                raise osv.except_osv(_('Error!'), _('At least one program should be asociated to this plan\n'))
        return True 
    
    def check_no_orphan_accounts(self, cr, uid, ids, context=None):
        #Verifies that every active budget account is included in the plan 
        for plan_id in ids:
            res = self.read(cr,uid,[plan_id],['program_ids'],context=context)[0]
            program_ids = res['program_ids']
            for program_id in program_ids:              
                query = 'SELECT BA.id, BA.code, BA.name FROM '\
                'budget_account BA '\
                'WHERE BA.account_type = \'%(account_type)s\' ' \
                'AND active = true '\
                'EXCEPT '\
                'SELECT BA.id, BA.code , BA.name FROM '\
                'budget_account BA INNER JOIN budget_program_line BPL ON BA.ID = BPL.account_id '\
                'INNER JOIN budget_program BP ON BPL.program_id = BP.id '\
                'WHERE BP.id = %(program_id)d' % {'program_id':program_id, 'account_type':'budget'}
                cr.execute(query)
                result = cr.fetchall()
                account_list = ''
                if result.__len__() > 0:
                    for line in result:
                        account_list = account_list + '%s - %s \n'  % (line[1],line[2])
                        program_obj = self.pool.get('budget.program').browse(cr,uid,[program_id],context=context)[0] 
                    raise osv.except_osv(_('Error!'), _('The following budget accounts are not listed in this program: \n '+ program_obj.name+ ": " + account_list   ))
        return True
    
    def check_no_consolidated_orphans(self, cr, uid, ids, context=None):
        query = 'SELECT code, name FROM budget_account '\
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
         if self.check_programs(cr, uid, ids, context=context):
             self.write(cr, uid, ids, {'state': 'confirmed'})
             return True     

    def action_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})
        return True
    
    def action_close(self, cr, uid, ids, context=None):
        period_obj = self.pool.get('account.period')
        
        for plan in self.browse(cr, uid, ids, context=context):
           period_ids = period_obj.search(cr, uid, [('date_start', '>=', plan.date_start), ('date_stop', '<=', plan.date_stop), ('special', '=', False)], context=context)
           for period in period_obj.browse(cr, uid, period_ids,context=context):
               if period.state != 'done':
                   raise osv.except_osv(_('Error!'), _('You cannot close a plan that has a period in draft state.\nThe period %s is in draft state.') % (period.name,))
        self.close_plan(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'closed'}, context=context)
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        for plan in self.browse(cr, uid,ids, context=context):
            if plan.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot delete an approved or closed plan'))
        return super(budget_plan, self).unlink(cr, uid, ids, context=context)
    
    def close_plan(self, cr, uid, ids, context=None):
        bud_move_obj= self.pool.get('budget.move')
        
        for plan in self.browse(cr, uid, ids, context=context):
            closeable_move_ids = self.get_budget_moves_for_close(cr, uid, plan.id, context=context)
            bud_move_obj.process_for_close(cr, uid, closeable_move_ids, plan.id, context=context)
            self.move_default_bud_program_line(cr, uid, ids , context=context)
            bud_move_obj.signal_workflow(cr, uid, [plan.id], 'button_close', context=context)
            self.hide_program_lines(cr, uid, ids , context=context)

    def hide_program_lines(self, cr, uid, plan_ids , context=None):
        mod_prog_lines=[]
        prog_line_obj= self.pool.get('budget.program.line')
        for plan_id in plan_ids:
            pl_search = prog_line_obj.search(cr, uid, [('program_id.plan_id.id', '=', plan_id )],context=context)
            prog_line_obj.write(cr, uid, pl_search, {'active_for_view':False})
            mod_prog_lines.append(pl_search)
        return mod_prog_lines


    def move_default_bud_program_line(self, cr, uid, plan_ids , context=None):
        mod_accounts=[]
        prog_line_obj= self.pool.get('budget.program.line')
        account_obj = self.pool.get('account.account')
        for plan_id in plan_ids:
            account_search = account_obj.search(cr, uid, [('default_budget_program_line','!=', None), ('default_budget_program_line.program_id.plan_id.id', '=', plan_id )],context=context)
            accounts=account_obj.browse(cr, uid, account_search,context=context)
            for acc in accounts: 
                next_program_line_id= prog_line_obj.get_next_year_line(cr, uid, [acc.default_budget_program_line.id], context=context)[acc.default_budget_program_line.id]
                if next_program_line_id:
                    account_obj.write(cr, uid, [acc.id], {'default_budget_program_line':next_program_line_id})
                    mod_accounts.append(acc.id)
        return mod_accounts


    def get_budget_moves_for_close(self, cr, uid, plan_id, context=None):
        query = 'SELECT DISTINCT BM.id FROM budget_move BM '\
                'INNER JOIN budget_move_line BML ON BML.budget_move_id=BM.id '\
                'INNER JOIN budget_program_line BPL ON BPL.id=BML.program_line_id '\
                'INNER JOIN budget_program BPR ON BPR.id=BPL.program_id '\
                'INNER JOIN budget_plan BP ON BP.id=BPR.plan_id '\
                'WHERE BM.state IN %s'\
                'AND BP.id = %s'
        params = (('draft', 'reserved', 'compromised', 'in_execution'), plan_id)
        cr.execute(query,params)
        result = [] 
        for line in cr.fetchall():
            result.append(line[0])
        return result
    

##
#ACCOUNT
##  
class budget_account(osv.osv):
    _name = 'budget.account'
    _description = 'Budget Account'
    _order = "parent_left"
    _parent_order = "code"
    _parent_store = True   

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
        
    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []

            if record.child_consol_ids:
                for acc in record.child_consol_ids:
                    if acc.id not in result[record.id]:
                        result[record.id].append(acc.id)
        return result
    
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
    
    def _get_children_and_consol(self, cr, uid, ids, context=None):
        #this function search for all the children and all consolidated children (recursively) of the given account ids
        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3
    
    def _get_all_children(self, cr, uid, ids, context=None):
        return self.search(cr, uid, [('parent_id', 'in', ids),'|',('active','=',True), ('active', '=',False)], context=context)
        

    def on_change_active(self, cr, uid, ids, active, context=None):
        if ids:
            return {'value': {},
                    'warning':{'title':'Warning','message':'This action will be applied to ALL children accounts'}}
        else:
            return {'value': {}}
    
    _columns ={
        'active':fields.boolean('Active'),
        'code': fields.char('Code', size=64, required=True, select=1),
        'name': fields.char('Name', size=256,),
        'account_type': fields.selection([
            ('budget', 'Budget Entry'),# CP
            ('view', 'Budget View'), # VP
            ('consolidation', 'Consolidation Entry'), # PC
            ('institutional', 'Institutional View'), # VI
        ], 'Internal Type', required=True, help="The 'Internal Type' is used for features available on "\
            "different types of accounts: view can not have journal items, consolidation are accounts that "\
            "can have children accounts for consolidations and can only have institutional views as parent, "\
            "institutional can have only consolidation childs"),
        'parent_id': fields.many2one('budget.account','Parent', ondelete="cascade"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'child_parent_ids': fields.one2many('budget.account','parent_id','Children'),
        'child_consol_ids': fields.many2many('budget.account', 'budget_account_consol_rel', 'parent_id' ,'consol_child_id' , 'Consolidated Children'),
        'child_id': fields.function(_get_child_ids, type='many2many', relation="budget.account", string="Child Accounts"),
        'allows_reimbursement':fields.boolean('Allows reimbursement'),
        'allows_reduction':fields.boolean('Allows reduction'),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'level': fields.function(_get_level, string='Level', method=True, type='integer',
             store={
                    'budget.account': (_get_children_and_consol, ['level', 'parent_id'], 10),
                   })
        }
    
    _defaults = {
        'account_type': 'budget',
        'active': True,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        'allows_reimbursement': False,
        'allows_reduction': False,
        
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
        
        for r in self.read(cr, uid, ids, ['code','name'], context):
            rec_name = '[%s] %s' % (r['code'], r['name'])
            res.append( (r['id'],rec_name) )
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like'):
            """We need all the partners that match with the ref or name (or a part of them)"""
            ids = self.search(cr, uid, ['|',('code', 'ilike', name),('name','ilike',name)] + args, limit=limit, context=context)
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
    
    def _used_by_program_line(self,cr,uid, account_id,context=None):
        obj_prog_line = self.pool.get('budget.program.line')
        ocurrences = obj_prog_line.search(cr,uid,[('account_id', '=', account_id)], context=context)
        if len(ocurrences) > 0:
            return True
        else:
            return False
        
    def unlink(self, cr, uid, ids, context=None):
        for account in self.browse(cr, uid,ids, context=context):
            if self._used_by_program_line(cr, uid, account.id, context=context):
                raise osv.except_osv(_('Error!'), _('You cannot delete an account used by a program line'))
            else:
                return super(budget_account, self).unlink(cr, uid, ids, context=context)
              
    def write(self, cr, uid, ids, vals, context=None):
        for account in self.browse(cr, uid,ids, context=context):
            if 'code' in vals.keys() or 'name' in vals.keys():
                if self._used_by_program_line(cr, uid, account.id, context=context):
                    raise osv.except_osv(_('Error!'), _('You cannot overwrite the code or the name of an account used by a program line'))
            if 'active' in vals.keys():
                children = self._get_all_children(cr,uid,[account.id],context=context)
                self.write(cr, uid, children, {'active':vals['active']},context=context)
        return super(budget_account, self).write(cr, uid, ids, vals, context=context)
        
