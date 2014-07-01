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
import decimal_precision as dp

from osv import fields, osv, orm


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
            bud_move_obj._workflow_signal(cr, uid, [plan.id], 'button_close', context=context)
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
#Program
## 
class budget_program(osv.osv):
    _name = 'budget.program'
    _description = 'Program'

    _columns ={
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=64, required=True),
        'plan_id': fields.many2one('budget.plan', 'Budget plan', required=True),
        'program_lines':fields.one2many('budget.program.line','program_id','Lines'),
        'previous_program_id': fields.many2one('budget.program', 'Previous program'),
        'state':fields.related('plan_id','state', type='char', relation='budget.plan',readonly=True ),
        }
    
    _sql_constraints = [
        ('name', 'unique(name,plan_id)','The name must be unique for this budget!'),
        ]
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        if not len(ids):
            return res
        
        for r in self.browse(cr, uid, ids, context):
            name = r.name
            stop_date = datetime.strptime(r.plan_id.date_stop, '%Y-%m-%d')
            year =datetime.strftime(stop_date, '%Y')
            rec_name = '%s(%s)' % (name, year)
            res.append( (r['id'],rec_name) )
        return res
    
    def make_composite_name(self,cr,uid,str):
        lst = []
        composite_name = ""
        space_pos = str.find(' ')
        if space_pos != -1:
            lst.append(str[0:space_pos])
            lst.append(str[space_pos+1:len(str)-1])
        else:
            lst.append(str[0:len(str)-1])  
        for word in lst:
            if len(word)>=3:
                composite_name = composite_name + word[0:3] +'-'
            else:
                composite_name = composite_name + word +'-'
        return composite_name[0:-1]

    def create(self, cr, uid, vals, context={}):
       plan_obj = self.pool.get('budget.plan')
       plan = plan_obj.browse(cr, uid, [vals['plan_id']],context=context)[0]
       stop_date = datetime.strptime(plan.date_stop, '%Y-%m-%d')
       year =datetime.strftime(stop_date, '%Y')
       code = year + '-' +  self.make_composite_name(cr,uid,vals['name'])
       vals['code'] = code

       if plan.state in ('approved', 'closed'):
           raise osv.except_osv(_('Error!'), _('You cannot create a program with a approved or closed plan'))
       
       res = super(budget_program, self).create(cr, uid, vals, context)
       return res

    def unlink(self, cr, uid, ids, context=None):
        for program in self.browse(cr, uid,ids, context=context):
            if program.plan_id.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot delete a program that is associated with an approved or closed plan '))
        return super(budget_program, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        for program in self.browse(cr, uid,ids, context=context):
            if program.plan_id.state in ('approved', 'closed'):
                raise osv.except_osv(_('Error!'), _('You cannot modify a program with a approved or closed plan'))
        return super(budget_program, self).write(cr, uid, ids, vals, context=context)

######################################################

##
#program LINE
##         
class budget_program_line(osv.osv):
    _name = 'budget.program.line'
    _description = 'Program line'
    _order = "parent_left"
    _parent_order = "name"
    _parent_store = True   

    def _get_children_and_consol(self, cr, uid, ids, context=None):
        #this function search for all the children and all consolidated children (recursively) of the given line ids
        if ids:
            ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        else:
            ids2 = []
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

    def add_unique(self,list_to_add, list):
        for item in list_to_add:
            if item not in list:
                list += [item]
        return list
    
    def __compute(self, cr, uid, ids, field_names, args, context=None):
        
        field_names = self.add_unique(['total_assigned','executed_amount','reserved_amount','modified_amount','extended_amount','compromised_amount'],field_names)
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)
        prg_lines = {}
        res = {}
        null_result = dict((fn, 0.0) for fn in field_names)
        if children_and_consolidated:
            
            mapping={ 
                     'total_assigned':'COALESCE(MAX(BPL.assigned_amount),0.0) AS total_assigned',
                     'executed':'COALESCE(SUM(BML.executed),0.0) AS executed_amount',
                     'reserved':'COALESCE(SUM(BML.reserved),0.0) AS reserved_amount',
                     'modified':'COALESCE(SUM(BML.modified),0.0) AS modified_amount',
                     'extended':'COALESCE(SUM(BML.extended),0.0) AS extended_amount',
                     'compromised':'COALESCE(SUM(BML.compromised),0.0) AS compromised_amount',
                }
            request = ('SELECT BPL.id, ' +\
                       ', '.join(mapping.values()) +
                    ' FROM budget_program_line BPL'\
                    ' LEFT OUTER JOIN budget_move_line BML ON BPL.id = BML.program_line_id'\
                    ' WHERE BPL.id IN %s'\
                    ' GROUP BY BPL.id') 
            params = (tuple(children_and_consolidated),)
            cr.execute(request, params)
            for row in cr.dictfetchall():
                prg_lines[row['id']] = row

            children_and_consolidated.reverse()
            brs = list(self.browse(cr, uid, children_and_consolidated, context=context))
            sums = {}
            currency_obj = self.pool.get('res.currency')
            while brs:
                current = brs.pop(0)
                
                for fn in field_names:
                    sums.setdefault(current.id, {})[fn] = prg_lines.get(current.id, {}).get(fn, 0.0)
                    for child in current.child_id:
                        if child.company_id.currency_id.id == current.company_id.currency_id.id:
                            sums[current.id][fn] += sums[child.id][fn]
                #   Thera are 2 types of available: 
                #    1-) available budget = assigned - opening + modifications + extensions - compromised - reserved - executed. 
                #    2-) available cash = assigned - opening + modifications + extensions - executed
   
                if 'available_cash' in field_names or 'available_budget' in field_names or'execution_percentage' in field_names:
                    available_budget = sums[current.id].get('total_assigned', 0.0) + sums[current.id].get('modified_amount', 0.0) + sums[current.id].get('extended_amount', 0.0) - sums[current.id].get('compromised_amount', 0.0) - sums[current.id].get('reserved_amount', 0.0) - sums[current.id].get('executed_amount', 0.0)
                    available_cash = sums[current.id].get('total_assigned', 0.0) + sums[current.id].get('modified_amount', 0.0) + sums[current.id].get('extended_amount', 0.0) - sums[current.id].get('executed_amount', 0.0)
                    
                    grand_total = (sums[current.id].get('total_assigned', 0.0) + sums[current.id].get('modified_amount', 0.0) + sums[current.id].get('extended_amount', 0.0))
                    exc_perc = grand_total != 0.0 and ((sums[current.id].get('executed_amount', 0.0)*100) /grand_total) or 0.0 
                    sums[current.id].update({'available_cash': available_cash, 'available_budget': available_budget, 'execution_percentage': exc_perc ,})

            for id in ids:
                res[id] = sums.get(id, null_result)
        else:
            for id in ids:
                res[id] = null_result
        return res

    def _check_unused_account(self, cr, uid, ids, context=None):
        #checks that the selected budget account is not associated to another program line
        for line in self.read(cr,uid,ids,['account_id','program_id']):
            cr.execute('SELECT count(1) '\
                        'FROM '+self._table+' '\
                        'WHERE account_id = %s '\
                        'AND id != %s'\
                        'AND program_id = %s',(line['account_id'][0],line['id'],line['program_id'][0]))
            
            if cr.fetchone()[0] > 0:        
                raise osv.except_osv(_('Error!'), _('There is already a program line using this budget account'))
        return True
        
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
    
    _columns ={
        'name':fields.char('Name', size=64, required=True),
        'parent_id': fields.many2one('budget.program.line', 'Parent line', ondelete='cascade'),
        'account_id':fields.many2one('budget.account','Budget account',required=True),
        'program_id':fields.many2one('budget.program','Program',required=True, ondelete='cascade'),
        'assigned_amount':fields.float('Assigned amount', digits_compute=dp.get_precision('Account'), required=True),
        'type':fields.related('account_id','account_type', type='char', relation='budget.account', string='Line Type', store=True,readonly=True  ),
        'state':fields.related('program_id','plan_id','state', type='char', relation='budget.plan',readonly=True ),
        'total_assigned':fields.function(__compute, string='Assigned', type="float", multi=True),
        'extended_amount':fields.function(__compute, string='Extensions', type="float", multi=True),
        'modified_amount':fields.function(__compute, string='Modifications', type="float", multi=True),
        'reserved_amount':fields.function(__compute, string='Reservations', type="float",multi=True),
        'compromised_amount':fields.function(__compute, string='Compromises', type="float", multi=True),
        'executed_amount':fields.function(__compute, string='Executed', type="float",multi=True),
        'available_budget':fields.function(__compute, string='Available Budget', type="float", multi=True),
        'available_cash':fields.function(__compute, string='Available Cash', type="float", multi=True),
        'execution_percentage':fields.function(__compute, string='Execution Percentage', type="float", multi=True),
        'sponsor_id':fields.many2one('res.partner','Sponsor'),
        'company_id':fields.many2one('res.company', 'Company', required=True),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'child_parent_ids': fields.one2many('budget.program.line','parent_id','Children'),
        'child_consol_ids': fields.many2many('budget.program.line', 'budget_program_line_consol_rel', 'parent_id' ,'consol_child_id' , 'Consolidated Children'),
        'child_id': fields.function(_get_child_ids, type='many2many', relation="budget.program.line", string="Child Accounts"),
        'previous_year_line_id': fields.many2one('budget.program.line','Previous year line'),
        'active_for_view': fields.boolean('Active')
        }
    
    _defaults = {
        'assigned_amount': 0.0,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'active_for_view': True
    }
     
    _constraints = [
        (_check_unused_account, 'Error!\nThe budget account is related to another program line.', ['account_id','program_id']),
    ]
    _sql_constraints = [
        ('name_uniq', 'unique(name, program_id,company_id)', 'The name of the line must be unique per company!'),
    ]
    def get_next_year_line(self, cr, uid, ids, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            result = self.search(cr, uid, [('previous_year_line_id','=',line.id)],context=context)
            if result:
                res[line.id]=result[0]
            else:
                res[line.id]=None
        return res
    
    def set_previous_year_line(self, cr, uid, ids, context=None):
        modified_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            previous_program_lines = self.search(cr, uid, [('program_id','=',line.program_id.previous_program_id.id),('account_id','=',line.account_id.id),],context=context)
            
            if previous_program_lines:
                self.write(cr, uid, [line.id], {'previous_year_line_id':previous_program_lines[0]}, context=context)
                modified_ids.append(line.id)
        return modified_ids
 
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid,ids, context=context):
            if line.program_id.plan_id.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot delete a line from an approved or closed plan'))
        return super(budget_program_line, self).unlink(cr, uid, ids, context=context)
    
    
    def write(self, cr ,uid, ids, vals,context=None):
        for line in self.browse(cr, uid,ids, context=context):
            if line.program_id.plan_id.state in ('approved','closed'):
               if len(vals) == 1 and 'active_for_view' in vals.keys():
                   pass  
               else:
                   raise osv.except_osv(_('Error!'), _('You cannot modify a line from an approved or closed plan'))
        return super(budget_program_line, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context={}):
       program_obj = self.pool.get('budget.program')
       program = program_obj.browse(cr, uid, [vals['program_id']],context=context)[0]
       
       if program.plan_id.state in ('approved', 'closed'):
           raise osv.except_osv(_('Error!'), _('You cannot create a line from an approved or closed plan'))
           
       return super(budget_program_line, self).create(cr, uid, vals, context)
   
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
        

##
# MOVE
## 

class budget_move(osv.osv):
    _name = "budget.move"
    _description = "Budget Move"
    
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('reserved', 'Reserved'),
        ('compromised', 'Compromised'),
        ('in_execution', 'In Execution'),
        ('executed', 'Executed'),
        ('transferred', 'Transferred'),
        ('cancel', 'Canceled'),
    ]
    
    MOVE_TYPE = [
    ('invoice_in',_('Purchase invoice')),
    ('invoice_out',_('Sale invoice')),
    ('manual_invoice_in',_('Manual purchase invoice')),
    ('manual_invoice_out',_('Manual sale invoice')),
    ('expense',_('Expense')),
    ('payroll',_('Payroll')),
    ('manual',_('From account move')),
    ('modification',_('Modification')),
    ('extension',_('Extension')),
    ('opening',_('Opening')),
    ]
        
    def distribution_get(self, cr, uid, ids, *args):
        amld_obj = self.pool.get('account.move.line.distribution')
        result = []
        search_ids= []
        for move in self.browse(cr, uid, ids):
            for bud_move_line in move.move_lines:
                
                search_ids = amld_obj.search(cr, uid, [('target_budget_move_line_id','=', bud_move_line.id)])
            result=result + search_ids
        return result

 
    def _compute_executed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids,context=context):
            total=0.0
            for line in move.move_lines:
                total += line.executed 
            res[move.id]= total 
        return res
    
    def _compute_compromised(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids,context=context):
            total=0.0
            for line in move.move_lines:
                total += line.compromised 
            res[move.id]= total 
        return res
    
    def _check_non_zero(self, cr, uid, ids, context=None):
        for obj_bm in  self.browse(cr, uid, ids, context=context):
            if (obj_bm.fixed_amount == 0.0 or obj_bm.fixed_amount == None) and obj_bm.standalone_move == True and obj_bm.state in ('draft','reserved'):
                return False
        return True
    
    def _calc_reserved(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for bud_move in self.browse(cr, uid, ids, context=context):
            res_amount = 0
            if bud_move.state == 'reserved':       
                for line in bud_move.move_lines:
                    res_amount += line.reserved
            else:
                res_amount = 0
            res[bud_move.id] = res_amount
        return res
    
    def _calc_reversed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for bud_move in self.browse(cr, uid, ids, context=context):
            res_amount = 0    
            for line in bud_move.move_lines:
                res_amount += line.reversed
            res[bud_move.id] = res_amount
        return res
    
    def recalculate_values(self, cr, uid, ids, context=None):
        mov_line_obj = self.pool.get('budget.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            move_fixed_total = 0.0
            for line in move.move_lines:
                mov_line_obj.write(cr, uid, [line.id], {'date' : line.date}, context=context)
                move_fixed_total += line.fixed_amount
            self.write(cr, uid, ids, {'date': move.date, 'fixed_amount': move_fixed_total}, context=context) 
    
    def _select_types(self,cr,uid,context=None):
        #In case that the move is created from the view "view_budget_move_manual_form", modifies the selectable types
        #reducing them to modification, extension and opening
        if context == None:
            context={}
        if context.get('standalone_move',False):
            return [('modification',_('Modification')),
                ('extension',_('Extension')),
                ('opening',_('Opening')),
                ]
        
        else:
            return [
                ('invoice_in',_('Purchase invoice')),
                ('invoice_out',_('Sale invoice')),
                ('manual_invoice_in',_('Manual purchase invoice')),
                ('manual_invoice_out',_('Manual sale invoice')),
                ('expense',_('Expense')),
                ('payroll',_('Payroll')),
                ('manual',_('From account move')),
                ('modification',_('Modification')),
                ('extension',_('Extension')),
                ('opening',_('Opening')),
                ]
            
    def _check_manual(self, cr, uid, context=None):
        if context.get('standalone_move',False):
            return True
        else:
            return False
    
    def _get_budget_moves_from_dist(self, cr, uid, ids, context=None):
        if ids:
            dist_obj = self.pool.get('account.move.line.distribution')
            dists = dist_obj.browse(cr, uid, ids, context = context)
            budget_move_ids = []
            for dist in dists:
                if dist.target_budget_move_line_id and \
                    dist.target_budget_move_line_id.budget_move_id and \
                    dist.target_budget_move_line_id.budget_move_id.id not in budget_move_ids:
                    budget_move_ids.append(dist.target_budget_move_line_id.budget_move_id.id)
            return budget_move_ids
        return []
    
    def _get_budget_moves_from_lines(self, cr, uid, ids, context=None):
        if ids:
            lines_obj = self.pool.get('budget.move.line')
            lines = lines_obj.browse(cr, uid, ids, context = context)
            budget_move_ids = []
            for line in lines:
                if line.budget_move_id and line.budget_move_id.id not in budget_move_ids:
                    budget_move_ids.append(line.budget_move_id.id)
            return budget_move_ids
        return []
    
    # Store triggers for functional fields
    STORE = {
        'budget.move':                      (lambda self, cr, uid, ids, context={}: ids, [], 10),
        'account.move.line.distribution':   (_get_budget_moves_from_dist, [], 10),
        'budget.move.line':                 (_get_budget_moves_from_lines, [], 10),
    }
    
    _columns = {
        'code': fields.char('Code', size=64, ),
        'name':fields.related('code', type='char'),
        'origin': fields.char('Origin', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'program_line_id': fields.many2one('budget.program.line', 'Program line', readonly=True, states={'draft':[('readonly',False)]},),
        'date': fields.datetime('Date created', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection(STATE_SELECTION, 'State', readonly=True, 
        help="The state of the move. A move that is still under planning is in a 'Draft' state. Then the move goes to 'Reserved' state in order to reserve the designated amount. This move goes to 'Compromised' state when the purchase operation is confirmed. Finally goes to the 'Executed' state where the amount is finally discounted from the budget available amount", select=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'fixed_amount' : fields.float('Fixed amount', digits_compute=dp.get_precision('Account'),),
        'standalone_move' : fields.boolean('Standalone move', readonly=True, states={'draft':[('readonly',False)]} ),
        'arch_reserved':fields.float('Original Reserved', digits_compute=dp.get_precision('Account'),),
        'reserved': fields.function(_calc_reserved, type='float', method=True, string='Reserved',readonly=True, store=STORE),
        'reversed': fields.function(_calc_reversed, type='float', method=True, string='Reversed',readonly=True, store=STORE),
        'arch_compromised':fields.float('Original compromised',digits_compute=dp.get_precision('Account'),),
        'compromised': fields.function(_compute_compromised, type='float', method=True, string='Compromised',readonly=True, store=STORE ),
        'executed': fields.function(_compute_executed, type='float', method=True, string='Executed',readonly=True, store=STORE ),
        'account_invoice_ids': fields.one2many('account.invoice', 'budget_move_id', 'Invoices' ),
        'move_lines': fields.one2many('budget.move.line', 'budget_move_id', 'Move lines' ),
        'budget_move_line_dist': fields.related('move_lines', 'budget_move_line_dist', type='one2many', relation="account.move.line.distribution", string='Account Move Line Distribution'),
        'type': fields.selection(_select_types, 'Move Type', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'previous_move_id': fields.many2one('budget.move', 'Previous move'),
        'from_migration':fields.boolean('Created from migration')
    }
    _defaults = {
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'standalone_move':_check_manual
    }
    
    def transfer_to_next_year(self, cr, uid, move_ids, plan_id, context=None):
        MOVE_RELATED_MODELS=['account.invoice',
                               'account.move',
                               'hr.expense.expense',
                               'hr.payslip',
                               'purchase.order',
                               ]
        obj_bud_line= self.pool.get('budget.move.line')
        obj_prog_line= self.pool.get('budget.program.line')
        for move in self.browse(cr, uid, move_ids, context=context):
            vals={
                  'origin':move.origin,
                  'company_id': move.company_id.id,
                  'fixed_amount':move.fixed_amount,
                  'standalone_move':move.standalone_move,
                  'arch_reserved':move.arch_reserved,
                  'arch_compromised':move.arch_compromised,
                  'type':move.type,
                  'previous_move_id':move.id,
                  'from_migration':True
                  }
            new_move_id = self.create(cr, uid, vals, context=context)
            for line in move.move_lines:
                if line.executed != line.fixed_amount:
                    prog_line_id=line.program_line_id.id
                    next_prog_line = obj_prog_line.get_next_year_line(cr, uid,  [prog_line_id], context=context)[prog_line_id]
                    if next_prog_line:
                        line_vals={
                                   'origin':line.origin,
                                   'budget_move_id':new_move_id,
                                   'program_line_id':next_prog_line,
                                   'date':line.date,
                                   'fixed_amount':line.fixed_amount,
                                   'line_available':line.line_available,
                                   'po_line_id': line.po_line_id.id,
                                   'so_line_id': line.so_line_id.id,
                                   'inv_line_id': line.inv_line_id.id,
                                   'expense_line_id': line.expense_line_id.id,
                                   'tax_line_id': line.tax_line_id.id,
                                   'payslip_line_id': line.payslip_line_id.id,
                                   'move_line_id': line.move_line_id.id,
                                   'account_move_id': line.account_move_id.id,
                                   'previous_move_line_id':line.id
                                   }
                        new_move_line_id = obj_bud_line.create(cr, uid, line_vals, context=context)
                        fields_to_blank ={
                                   'po_line_id': None,
                                   'so_line_id': None,
                                   'inv_line_id': None,
                                   'expense_line_id': None,
                                   'tax_line_id': None,
                                   'payslip_line_id': None,
                                   'move_line_id': None,
                                   'account_move_id': None,
                                   }
                        obj_bud_line.write(cr, uid, [line.id], fields_to_blank, context=context)
            self.replace_budget_move(cr, uid, move.id, new_move_id, MOVE_RELATED_MODELS,context=context )
    
            if move.state == 'compromised':
                self._workflow_signal(cr, uid, [new_move_id], 'button_reserve', context=context)
                self._workflow_signal(cr, uid, [new_move_id], 'button_compromise', context=context)
            if move.state == 'in_execution':
                self._workflow_signal(cr, uid, [new_move_id], 'button_execute', context=context)
            
    def replace_budget_move(self, cr, uid, old_id, new_id, models,context=None ):
        for model in models:
            obj=self.pool.get(model)
            search_result = obj.search(cr, uid, [('budget_move_id','=',old_id)], context=context)
            obj.write(cr, uid, search_result, {'budget_move_id': new_id})
    
    def process_for_close(self, cr, uid, closeable_move_ids, plan_id, context=None):
        for move in self.browse(cr, uid, closeable_move_ids, context=context):
            if move.state in ('draft', 'reserved'):
                self._workflow_signal(cr, uid, [move.id], 'button_cancel', context=context)
            if move.state in ('compromised', 'in_execution'):
                self.transfer_to_next_year(cr, uid, [move.id], plan_id, context=context)
                self._workflow_signal(cr, uid, [move.id], 'button_transfer', context=context)

    def _check_values(self, cr, uid, ids, context=None):
        list_line_ids_repeat = []
        
        for move in self.browse(cr, uid, ids, context=context):
            if  move.type in ('invoice_in','manual_invoice_in','expense', 'opening','extension') and move.fixed_amount <= 0:
                return [False,_('The reserved amount must be positive')]
            if  move.type in ('payroll') and move.fixed_amount < 0:
                return [False,_('The reserved amount must be positive')]
            if  move.type in ('invoice_out','manual_invoice_out') and move.fixed_amount >= 0:
                return [False,_('The reserved amount must be negative')]
            if  move.type in ('modifications') and move.fixed_amount != 0:
                return [False,_('The sum of addition and subtractions from program lines must be zero')]
            
            #Check if exist a repeated program_line
            if move.standalone_move == True:                
                for line in move.move_lines:
                    list_line_ids_repeat.append(line.program_line_id.id)
                
                list_line_ids = list(set(list_line_ids_repeat)) #Delete repeated items
                
                if len(list_line_ids_repeat) > len(list_line_ids):
                    return [False,_('Program lines in budget move lines cannot be repeated')]
            
            #Check amount for each move_line
            for line in move.move_lines:
                if line.type =='extension':
                    if line.fixed_amount < 0 :
                        return [False, _('An extension amount cannot be negative')]
                elif line.type =='modification':
                    if (line.fixed_amount < 0) & (line.program_line_id.available_budget < abs(line.fixed_amount)):
                        return [False, _('The amount to substract from ') + line.program_line_id.name + _(' is greater than the available ')]
                elif line.type in ('opening','manual_invoice_in', 'expense', 'invoice_in', 'manual'):
                    if line.program_line_id.available_budget < line.fixed_amount:
                        return [False, _('The amount to substract from ') + line.program_line_id.name + _(' is greater than the available ')]
        return [True,'']
    
    def create(self, cr, uid, vals, context={}):
        bud_program_lines_obj = self.pool.get('budget.program.line')
        bud_program_lines = []
        
        if 'code' not in vals.keys():
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'budget.move')
        else:
            if vals['code']== None or vals['code'] == '':
                vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'budget.move')
        
        #Extract program_line_id from values (move_lines is a budget move line list)
        for bud_line in vals.get('move_lines',[]):
            #position 3 is a dictionary, extract program_line_id value
            program_line_id = bud_line[2]['program_line_id']
            bud_program_lines.append(program_line_id)
                
        for line in bud_program_lines_obj.browse(cr, uid, bud_program_lines, context=context):
            if line.program_id.plan_id.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot create a budget move that have associated budget move lines with a approved or closed budget plan'))
        
        res = super(budget_move, self).create(cr, uid, vals, context)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        super(budget_move,self).write(cr, uid, ids, vals, context=context)
        for bud_move in self.browse(cr, uid, ids, context=context):
            if bud_move.state in ('reserved','draft') and bud_move.standalone_move :       
                res_amount=0
                for line in bud_move.move_lines:
                    res_amount += line.fixed_amount
                vals['fixed_amount'] = res_amount
                return super(budget_move,self).write(cr, uid, ids, {'fixed_amount':res_amount}, context=context)
        
    def on_change_move_line(self, cr, uid, ids, move_lines, context=None):
        res={}
        res_amount=0.0
        for move in self.browse(cr, uid, ids, context=context):
            if move.standalone_move:
                res_amount=0.0
                for line in move.move_lines:
                        res_amount += line.fixed_amount
        return {'value':{ 'fixed_amount':res_amount }}
            
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def action_reserve(self, cr, uid, ids, context=None):
        result = self._check_values(cr, uid, ids, context)#check positive or negative for different types of moves
        obj_mov_line = self.pool.get('budget.move.line')
        if result[0]:
            self.write(cr, uid, ids, {'state': 'reserved'})
            self.recalculate_values(cr, uid, ids, context=context)
        else:
            raise osv.except_osv(_('Error!'), result[1])
        return True
            
    def action_compromise(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid,ids, context=context):
            self.write(cr, uid, ids, {'state': 'compromised'})
            self.recalculate_values(cr, uid, ids, context=context)
            self.write(cr, uid, ids, {'arch_compromised': move.compromised, })
        return True
    
    def action_in_execution(self, cr, uid, ids, context=None):
        result = self._check_values(cr, uid, ids, context)
        if result[0]:
            self.write(cr, uid, ids, {'state': 'in_execution'})
            self.recalculate_values(cr, uid, ids, context=context)
        else:
            raise osv.except_osv(_('Error!'), result[1])
        return True
    
    def action_execute(self, cr, uid, ids, context=None):
        obj_mov_line = self.pool.get('budget.move.line')
        for move in self.browse(cr, uid,ids, context=context):
            self.write(cr, uid, [move.id], {'state': 'executed'})
            for line in move.move_lines:
                self.recalculate_values(cr, uid, ids, context=context)
            self.write(cr, uid, [move.id], {'state': 'executed'})
        return True
            
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.recalculate_values(cr, uid, ids, context=context)
        return True
    
    def action_transfer(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'transferred'})
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []    
        if not len(ids):
            return res
            
        for r in self.read(cr, uid, ids, ['code'], context):
            rec_name = '%s' % (r['code']) 
            res.append( (r['id'],rec_name) )
        return res
    
    def is_executed(self, cr, uid, ids, *args):
        dist_obj = self.pool.get('account.move.line.distribution') 
        executed = 0.0
        void = 0.0
        for move in self.browse(cr, uid, ids,):
            if move.type in ('opening','extension','modification'):
                if move.state == 'in_execution':
                    return True
            if move.type in ('manual_invoice_in','expense','invoice_in', 'payroll', 'manual'):
                distr_line_ids = []
                for line in move.move_lines:
                    distr_line_ids += dist_obj.search(cr, uid,[('target_budget_move_line_id','=',line.id)])
                for dist in dist_obj.browse(cr, uid, distr_line_ids):
                    if dist.account_move_line_type =='liquid':
                        executed += dist.distribution_amount
                    elif dist.account_move_line_type =='void':
                        void += dist.distribution_amount
                        
                if executed == move.fixed_amount - void:
                    return True
        return False
    
    def is_in_execution(self, cr, uid, ids, *args):
        dist_obj = self.pool.get('account.move.line.distribution') 
        executed = 0.0
        void = 0.0
        for move in self.browse(cr, uid, ids,):
            if move.type in ('opening','extension','modification'):
                    return False
            if move.type in ('manual_invoice_in','expense','invoice_in', 'payroll', 'manual'):
                distr_line_ids = []
                for line in move.move_lines:
                    distr_line_ids += dist_obj.search(cr, uid,[('target_budget_move_line_id','=',line.id)])
                for dist in dist_obj.browse(cr, uid, distr_line_ids):
                    if dist.account_move_line_type =='liquid':
                        executed += dist.distribution_amount
                    elif dist.account_move_line_type =='void':
                        void += dist.distribution_amount
                        
                if executed != move.fixed_amount - void:
                    return True
        return False
    
    def dummy_button(self,cr,uid, ids,context=None):
        return True   
    
    def unlink(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'draft':
                raise osv.except_osv(_('Error!'), _('Orders in state other than draft cannot be deleted \n'))
            for line in move.move_lines:
                if line.program_line_id.program_id.plan_id.state in ('approved','closed'):
                    raise osv.except_osv(_('Error!'), _('You cannot delete a budget move budget move that have associated budget lines with a approved or closed budget plan'))
           
		super(budget_move,self).unlink(cr, uid, ids, context=context)


class budget_move_line(osv.osv):
    _name = "budget.move.line"
    _description = "Budget Move Line"
    
    def on_change_program_line(self, cr, uid, ids, program_line, context=None):
        for line in self.pool.get('budget.program.line').browse(cr, uid,[program_line], context=context):
            return {'value': {'line_available':line.available_budget},}
        return {'value': {}}
    
    def _compute(self, cr, uid, ids, field_names, args, context=None, ignore_dist_ids=[]):
        amld = self.pool.get('account.move.line.distribution')
        fields = ['compromised', 'executed','reversed', 'reserved']
        res = {}
        lines = self.browse(cr, uid, ids,context=context)
         
        for line in lines:
            res[line.id] = {}
            executed = 0.0
            compromised = 0.0
            reversed = 0.0
            reserved = 0.0
            if line.state in ('executed','in_execution','transferred'):
                if line.type == 'opening':
                    executed = line.fixed_amount
                    
                elif line.type in ('manual_invoice_in','expense','invoice_in','payroll','manual'):
                    line_ids_bar = amld.search(cr, uid, [('target_budget_move_line_id','=', line.id),('account_move_line_type','=','liquid')], context=context)
                    for bar_line in amld.browse(cr, uid, line_ids_bar, context=context):
                        if bar_line.id in ignore_dist_ids:
                            continue
                        executed += bar_line.distribution_amount
            
            void_line_ids_amld = amld.search(cr, uid, [('target_budget_move_line_id','=', line.id),('account_move_line_type','=','void')], context=context)
            for void_line in amld.browse(cr, uid, void_line_ids_amld, context=context):
                if void_line.id in ignore_dist_ids:
                    continue
                reversed += void_line
            
            if line.previous_move_line_id:
                executed = executed + line.previous_move_line_id.executed
                reversed = reversed + line.previous_move_line_id.reversed
                        
            if line.state in ('compromised','executed','in_execution','transferred'):
                compromised = line.fixed_amount - executed - line.reversed
            
            if line.state == 'reserved':
                    reserved = line.fixed_amount - reversed
                
            res[line.id]['executed'] = executed
            res[line.id]['compromised'] = compromised 
            res[line.id]['reversed'] = reversed
            res[line.id]['reserved'] = reserved 
        return res
    
    def compute(self, cr, uid, ids, field_names, args, context=None, ignore_dist_ids=[]):
        return self._compute(cr, uid, ids, field_names, args, context, ignore_dist_ids)

    def _compute_modified(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        lines = self.browse(cr, uid, ids,context=context) 
        for line in lines:
            total = 0.0
            if line.state == 'executed':
                if line.type == 'modification':
                    total = line.fixed_amount
            res[line.id]= total 
        return res
    
    def _compute_extended(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        lines = self.browse(cr, uid, ids,context=context) 
        for line in lines:
            total = 0.0
            if line.state == 'executed':
                if line.type == 'extension':
                    total = line.fixed_amount
            res[line.id]= total 
        return res
    
    def _check_non_zero(self, cr, uid, ids, context=None):
        for obj_bm in  self.browse(cr, uid, ids, context=context):
            if (obj_bm.fixed_amount == 0.0 or obj_bm.fixed_amount == None) and obj_bm.standalone_move == True and obj_bm.state in ('draft','reserved'):
                return False
        return True
    
    def _check_plan_state(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            if line.program_line_id.state != 'approved':
                if not line.from_migration:
                    next_line = self.get_next_year_line(cr, uid, [line.id], context=context)[line.id]
                    if not next_line:
                        return False
                
        return True
        
    def _line_name(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        lines = self.browse(cr, uid, ids,context=context) 
        for line in lines:
            name = line.budget_move_id.code+ "\\" + line.origin 
            res[line.id]= name 
        return res
    
    
    _columns = {
        'origin': fields.char('Origin', size=64, ),
        'budget_move_id': fields.many2one('budget.move', 'Budget Move', required=True, ondelete='cascade'),
        'name': fields.function(_line_name, type='char', method=True, string='Name',readonly=True, store=True),
        'code': fields.related('origin', type='char', size=64, string = 'Origin'),
        'program_line_id': fields.many2one('budget.program.line', 'Program line', required=True),
        'date': fields.datetime('Date created', required=True,),
        'fixed_amount': fields.float('Original amount',digits_compute=dp.get_precision('Account'),),
        'line_available':fields.float('Line available',digits_compute=dp.get_precision('Account'),readonly=True),
        'modified': fields.function(_compute_modified, type='float', method=True, string='Modified',readonly=True, store=True),
        'extended': fields.function(_compute_extended, type='float', method=True, string='Extended',readonly=True, store=True),
        'reserved': fields.function(_compute, type='float', method=True, multi=True, string='Reserved',readonly=True, store=True),
        'reversed': fields.function(_compute, type='float', method=True, multi=True, string='Reversed',readonly=True, store=True),
        'compromised': fields.function(_compute, type='float', method=True, multi=True, string='Compromised', readonly=True, store=True),
        'executed': fields.function(_compute, type='float', method=True, multi=True, string='Executed',readonly=True, store=True),
        'po_line_id': fields.many2one('purchase.order.line', 'Purchase order line', ),
        'so_line_id': fields.many2one('sale.order.line', 'Sale order line', ),
        'inv_line_id': fields.many2one('account.invoice.line', 'Invoice line', ),
        'expense_line_id': fields.many2one('hr.expense.line', 'Expense line', ),
        'tax_line_id': fields.many2one('account.invoice.tax', 'Invoice tax line', ),
        'payslip_line_id': fields.many2one('hr.payslip.line', 'Payslip line', ),
        'move_line_id': fields.many2one('account.move.line', 'Move line', ),
        'account_move_id': fields.many2one('account.move', 'Account Move', ),
        'type': fields.related('budget_move_id', 'type', type='char', relation='budget.move', string='Type', readonly=True),
        'state': fields.related('budget_move_id', 'state', type='char', relation='budget.move', string='State',  readonly=True),
        #=======bugdet move line distributions
        'budget_move_line_dist': fields.one2many('account.move.line.distribution','target_budget_move_line_id', 'Budget Move Line Distributions'),
        'type_distribution':fields.related('budget_move_line_dist','type', type="selection", relation="account.move.line.distribution", string="Distribution type"),
        #=======Payslip lines
        'previous_move_line_id': fields.many2one('budget.move', 'Previous move line'),
        'from_migration':fields.related('budget_move_id','from_migration', relation='budget.move', string='Transferred', readonly=True)

    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'reversed': 0.0,
        'from_migration':False
        }
    
    _constraints=[
        (_check_plan_state, 'Error!\n The plan for this program line must be in approved state', ['fixed_amount','type']),
        ]
    
    def get_next_year_line(self, cr, uid, ids, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            result = self.search(cr, uid, [('previous_move_line_id','=',line.id)],context=context)
            if result:
                res[line.id]=result[0]
            else:
                res[line.id]=None
        return res
    
    def create(self, cr, uid, vals, context={}):
        program_line_obj = self.pool.get('budget.program.line')
        program_line = program_line_obj.browse(cr, uid, [vals['program_line_id']],context=context)[0]
       
        if program_line.program_id.plan_id.state in ('cancel', 'closed'):
           raise osv.except_osv(_('Error!'), _('You cannot create a budget move line from an cancel or closed plan'))
        return super(budget_move_line, self).create(cr, uid, vals, context)
       
    def write(self, cr, uid, ids, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        
        for bud_move_line in self.browse(cr, uid, ids, context=context):
             if bud_move_line.program_line_id.program_id.plan_id.state in ('cancel','closed'):
                 next_line = self.get_next_year_line(cr, uid, [bud_move_line.id], context=context)[bud_move_line.id]
                 if not next_line:
                     raise osv.except_osv(_('Error!'), _('You cannot create a budget move line with a canceled or closed plan'))
            
        super(budget_move_line, self).write(cr, uid, ids, vals, context=context)
        
        next_year_lines = self.get_next_year_line(cr, uid, ids, context=context)
        for line_id in next_year_lines.keys():
            if next_year_lines[line_id]:
                next_line =self.browse(cr, uid, [next_year_lines[line_id]], context=context)[0]
                bud_move_obj.recalculate_values(cr, uid,[next_line.budget_move_id.id], context=context)
    

    def unlink(self, cr, uid, ids, context=None):
        for bud_move_line in self.browse(cr, uid, ids, context=context):
             if bud_move_line.program_line_id.program_id.plan_id.state in ('cancel','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot create a budget move with a canceled or closed plan'))
        super(budget_move_line, self).unlink(cr, uid, ids, context=context)

class account_move_line_distribution(orm.Model):
    _name = "account.move.line.distribution"
    _description = "Account move line distribution"

    _columns = {         
         'account_move_line_id': fields.many2one('account.move.line', 'Account Move Line', ondelete="cascade"),
         'distribution_percentage': fields.float('Distribution Percentage', required=True, digits_compute=dp.get_precision('Account'),),
         'distribution_amount': fields.float('Distribution Amount', digits_compute=dp.get_precision('Account'), required=True),
         'target_budget_move_line_id': fields.many2one('budget.move.line', 'Target Budget Move Line',),
         'target_account_move_line_id': fields.many2one('account.move.line', 'Target Budget Move Line'),
         'reconcile_ids': fields.many2many('account.move.reconcile','bud_reconcile_distribution_ids'),
         'type': fields.selection([('manual', 'Manual'),('auto', 'Automatic')], 'Distribution Type', select=True),
         'account_move_line_type': fields.selection([('liquid', 'Liquid'),('void', 'Void')], 'Budget Type', select=True),
    }
    
    _defaults = {
        'type': 'manual', 
        'distribution_amount': 0.0,
        'distribution_percentage': 0.0,
    }

    #====== Check the plan for distribution line
    def get_plan_for_distributions(self, cr, uid, dist_ids, context=None):
       query = 'SELECT AMLD.id AS dist_id, BP.id AS plan_id FROM account_move_line_distribution AMLD '\
               'INNER JOIN budget_move_line BML ON AMLD.target_budget_move_line_id = BML.id '\
               'INNER JOIN  budget_move BM ON BML.budget_move_id=BM.id '\
               'INNER JOIN budget_program_line BPL ON BPL.id=BML.program_line_id '\
               'INNER JOIN budget_program BPR ON BPR.id=BPL.program_id '\
               'INNER JOIN budget_plan BP ON BP.id=BPR.plan_id '\
               'WHERE AMLD.id IN %s'
       params = (tuple(dist_ids),)
       cr.execute(query,params)
       result = cr.dictfetchall()
       
       return result
    
    def _check_plan_distribution_line(self, cr, uid, ids, context=None):
        
        plan_obj = self.pool.get('budget.plan')
        
        #Get plan for distribution lines 
        result = self.get_plan_for_distributions(cr, uid, ids, context)
                
        #Check plan's state
        for dist_id in result:
            plan = plan_obj.browse(cr, uid, [dist_id['plan_id']], context=context)[0]
            if plan.state in ('closed'):
                 return False
        return True

    #A distribution line only has one target. This target can be a move_line or a budget_line
    def _check_target_move_line (self, cr, uid, ids, context=None):
        distribution_line_obj = self.browse(cr, uid, ids[0],context)
        
        if distribution_line_obj.target_budget_move_line_id and distribution_line_obj.target_account_move_line_id:
            return False
        else:
            return True
    
    #======== Distribution amount must be less than compromised amount in budget move line
    def _check_distribution_amount_budget(self, cr, uid, ids, context=None):
        for distribution in self.browse(cr,uid,ids,context=context):
            computes = self.pool.get('budget.move.line').compute(cr, uid, [distribution.target_budget_move_line_id.id], ['compromised'], None, context=context, ignore_dist_ids=[distribution.id])
            compromised = round(computes[distribution.target_budget_move_line_id.id]['compromised'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account'))
            if abs(distribution.distribution_amount) > abs(compromised):
                return False
            return True  
    
    #======== Check distribution percentage. Use distribution_percentage_sum in account.move.line to check 
    def _check_distribution_percentage(self, cr, uid, ids, context=None):          
        
        for distribution in self.browse(cr, uid, ids, context=context):
            #distribution_percentage_sum compute all the percentages for a specific move line. 
            line_percentage = distribution.account_move_line_id.distribution_percentage_sum or 0.0
            line_percentage_remaining = 100 - line_percentage
            
            if distribution.distribution_percentage > line_percentage_remaining:
                return False
            
            return True
        
    #========= Check distribution percentage. Use distribution_amount_sum in account.move.line to check 
    def _check_distribution_amount(self, cr, uid, ids, context=None):          
        amount = 0.0
        
        for distribution in self.browse(cr, uid, ids, context=context):
            #==== distribution_amount_sum compute all the percentages for a specific move line. 
            x = distribution.account_move_line_id
            y = distribution.account_move_line_id.id
            line_amount_dis = distribution.account_move_line_id.distribution_amount_sum or 0.0
            
            #=====Find amount for the move_line
            if distribution.account_move_line_id.credit > 0:
                amount = distribution.account_move_line_id.credit
            if distribution.account_move_line_id.debit > 0:
                amount = distribution.account_move_line_id.debit
            if distribution.account_move_line_id.credit == 0 and distribution.account_move_line_id.debit == 0:
                amount = distribution.account_move_line_id.fixed_amount
            
            #====Check which is the remaining between the amount line and sum of amount in distributions. 
            amount_remaining = amount - line_amount_dis
            
            if distribution.distribution_amount > amount_remaining:
                return False            
            return True
    
    #==================================================================================
    _constraints = [
        (_check_target_move_line,'A Distribution Line only has one target. A target can be a move line or a budget move line',['target_budget_move_line_id', 'target_account_move_line_id']),
        (_check_distribution_amount_budget, 'The distribution amount can not be greater than compromised amount in budget move line selected', ['distribution_amount']),
        (_check_distribution_percentage, 'The distribution percentage can not be greater than sum of all percentage for the account move line selected', ['account_move_line_id']),    
        (_check_distribution_amount, 'The distribution amount can not be greater than maximum amount of remaining amount for account move line selected', ['distribution_amount']),    
        (_check_plan_distribution_line, 'You cannot create a distribution with a approved or closed plan',['distribution_amount']),    
    ]

    def clean_reconcile_entries(self, cr, uid, move_line_ids, context=None):
        lines = []
        for move_line_id in move_line_ids:
            result = self.search(cr ,uid, [('account_move_line_id','=', move_line_id)], context=context)
            lines += result
        self.unlink(cr, uid, lines,context=context)
        return True

    def _account_move_lines_mod(self, cr, uid, ids, context=None):
        list = []
        for line in self.browse(cr, uid, ids, context=context):
            list.append(line.account_move_line_id.id)
        return list
        
    def create(self, cr, uid, vals, context=None):
        if context:
            dist_type = context.get('distribution_type','auto')
        else:
            dist_type = 'auto'
        vals['type'] = dist_type
        res = super(account_move_line_distribution, self).create(cr, uid, vals, context)
        return res   

    def write(self, cr, uid, ids, vals, context=None):       
        plan_obj = self.pool.get('budget.plan')
        
        #Get plan for distribution lines 
        result = self.get_plan_for_distributions(cr, uid, ids, context)
                

        #Check plan's state
        for dist_id in result:
            plan = plan_obj.browse(cr, uid, [dist_id['plan_id']], context=context)[0]
            if plan.state in ('closed'):
                 raise osv.except_osv(_('Error!'), _('You cannot modify a distribution with a closed plan'))
                    
        super(account_move_line_distribution, self).write(cr, uid, ids, vals, context=context)
    
    def unlink(self, cr, uid, ids, context=None,is_incremental=False):
        plan_obj = self.pool.get('budget.plan')
        bud_move_obj = self.pool.get('budget.move')
        if ids:
            result = self.get_plan_for_distributions(cr, uid, ids, context)
                    
            #Check plan's state
            for dist_id in result:
                plan = plan_obj.browse(cr, uid, [dist_id['plan_id']], context=context)[0]
                if plan.state in ('closed'):
                    if not is_incremental:
                        raise osv.except_osv(_('Error!'), _('You cannot delete a distribution with a closed plan'))   
            move_ids=[]
            for dist in self.browse(cr, uid, ids, context=context):
                if dist.target_budget_move_line_id:
                    move_ids.append(dist.target_budget_move_line_id.budget_move_id.id)
            super(account_move_line_distribution, self).unlink(cr, uid, ids, context=context)
            bud_move_obj.recalculate_values(cr, uid,move_ids, context=context)
               
        
    

