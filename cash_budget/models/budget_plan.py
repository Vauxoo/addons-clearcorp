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
    _name = 'cash.budget.plan'
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
        'program_ids':fields.one2many('cash.budget.program','plan_id','Programs'),
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
                        program_obj = self.pool.get('cash.budget.program').browse(cr,uid,[program_id],context=context)[0]
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
        bud_move_obj= self.pool.get('cash.budget.move')
        
        for plan in self.browse(cr, uid, ids, context=context):
            closeable_move_ids = self.get_budget_moves_for_close(cr, uid, plan.id, context=context)
            bud_move_obj.process_for_close(cr, uid, closeable_move_ids, plan.id, context=context)
            self.move_default_bud_program_line(cr, uid, ids , context=context)
            bud_move_obj.signal_workflow(cr, uid, [plan.id], 'button_close', context=context)
            self.hide_program_lines(cr, uid, ids , context=context)

    def hide_program_lines(self, cr, uid, plan_ids , context=None):
        mod_prog_lines=[]
        prog_line_obj= self.pool.get('cash.budget.program.line')
        for plan_id in plan_ids:
            pl_search = prog_line_obj.search(cr, uid, [('program_id.plan_id.id', '=', plan_id )],context=context)
            prog_line_obj.write(cr, uid, pl_search, {'active_for_view':False})
            mod_prog_lines.append(pl_search)
        return mod_prog_lines


    def move_default_bud_program_line(self, cr, uid, plan_ids , context=None):
        mod_accounts=[]
        prog_line_obj= self.pool.get('cash.budget.program.line')
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
    
