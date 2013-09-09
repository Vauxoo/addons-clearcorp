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
    _columns ={
        'name': fields.char('Name', size=64, required=True),
        'year_id': fields.many2one('budget.year','Year',required=True),
        'state':fields.selection(STATE_SELECTION, 'State', readonly=True, 
        help="The state of the bugdet. A budget that is still under planning is in a 'Draft' state. Then the plan has to be confirmed by the user in order to be approved, the state switch to 'Confirmed'. Then the manager must confirm the budget plan to change the state to 'Approved'. If a plan will not be approved it must be cancelled.", select=True),
        'program_ids':fields.one2many('budget.program','plan_id','Programs'),
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
#                query = 'SELECT BA.id, BA.composite_code, BA.name FROM '\
#                'budget_account BA '\
#                'WHERE BA.account_type = \'%(account_type)s\' ' \
#                'AND active = true '\
#                'EXCEPT '\
#                'SELECT BA.id, BA.composite_code , BA.name FROM '\
#                'budget_account BA INNER JOIN budget_program_line BPL ON BA.ID = BPL.account_id '\
#                'INNER JOIN budget_program BP ON BPL.program_id = BP.id '\
#                'WHERE BP.id = %(program_id)d' % {'program_id':program_id, 'account_type':'budget'}
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
#        query = 'SELECT composite_code, name FROM budget_account '\
#                'WHERE id IN( '\
#                'SELECT id FROM budget_account '\
#                'WHERE account_type = \'budget\' '\
#                'EXCEPT '\
#                'SELECT DISTINCT consol_child_id '\
#                'FROM budget_account_consol_rel) '
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
#        if self.check_no_orphan_accounts(cr, uid, ids, context=context):
#            if self.check_no_consolidated_orphans(cr, uid, ids, context=context):
         if self.check_programs(cr, uid, ids, context=context):
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
    
#    def bulk_line_create(self, cr, uid, ids, context=None):            
#        line_obj = self.pool.get('budget.program.line')
#        account_obj = self.pool.get('budget.account')
#        for program in self.browse(cr, uid, ids, context=context):
#            current_lines = len(program.program_lines)
#            if current_lines > 0:
#                raise osv.except_osv(_('Error!'), _('This program already contains program lines'))   
#            account_ids= account_obj.search(cr,uid,[('active','=','true'),('account_type','=','budget')])
#            for account in account_obj.browse(cr,uid,account_ids):
##                line_name = '[' + account.composite_code + ']-' + account.name 
#                line_name = '[' + account.code + ']-' + account.name
#                line_account_id = account.id
#                line_program_id = program.id
#                line_obj.create(cr,uid,{
#                                        'name':line_name,
#                                        'account_id':line_account_id,
#                                        'program_id':line_program_id,                                                                              
#                                        })
#        return True
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
       
       code = plan.year_id.code + '-' +  self.make_composite_name(cr,uid,vals['name'])
       vals['code'] = code
       res = super(budget_program, self).create(cr, uid, vals, context)
       return res



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
        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

#    def get_assigned(self, cr, uid, ids, field_name, args, context=None):
#        test = {}
#        for line in self.browse(cr, uid, ids,context=context):
#            children_and_consolidated = self._get_children_and_consol(cr, uid,[line.id],context=context)
#            request = ("SELECT SUM(assigned_amount) " +\
#                           " FROM budget_program_line l" \
#                           " WHERE l.id IN %s ")
#            params = (tuple(children_and_consolidated),)
#            cr.execute(request, params)
#            result = cr.fetchall()
#        
#            if len(result) > 0:
#                for row in result:
#                    test[line.id]=row[0]                
#        return test
    

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
#                params = (tuple(ids),)
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

        
#            if len(result) > 0:
#                for row in result:
#                    test[line.id]=row[0]                
#        return test
    
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
        'program_id':fields.many2one('budget.program','Program',required=True, on_delete='cascade'),
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
        #'currency_id':fields.many2one('res.currency', string='Currency', readonly=True)
        }
    
    _defaults = {
        'assigned_amount': 0.0,         
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        #'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id,
    }
     
    _constraints = [
        (_check_unused_account, 'Error!\nThe budget account is related to another program line.', ['account_id','program_id']),
    ]
    _sql_constraints = [
        ('name_uniq', 'unique(name, program_id,company_id)', 'The name of the line must be unique per company!'),
    ]
    
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid,ids, context=context):
            if line.program_id.plan_id.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot delete a line from an approved or closed plan'))
        return super(budget_program_line, self).unlink(cr, uid, ids, context=context)
    
    
    def write(self, cr ,uid, ids, vals,context=None):
        for line in self.browse(cr, uid,ids, context=context):
            if line.program_id.plan_id.state in ('approved','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot modify a line from an approved or closed plan'))
        return super(budget_program_line, self).write(cr, uid, ids, vals, context=context)

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
        #'composite_code': fields.function(get_composite_code, string='Full Code', type="char", store=True),
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
#            ids = self.search(cr, uid, ['|',('composite_code', 'ilike', name),('name','ilike',name)] + args, limit=limit, context=context)
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
    
#    def _cascade_activate_deactivate(self, cr, uid, ids, val, context=None):
#        for account in self.browse(cr, uid, ids, context=context):
#            children = self._get_children(cr, uid, [account.id], context=context)
#            self.write(cr, uid, children, { 'active':val }, context)
#            
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
                raise osv.except_osv(_('Error!'), _('There is no budget year defined for this date.\nPlease create one from the configuration of the budget menu.'))
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
        
    def _compute_executed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        total=0.0
        for move in self.browse(cr, uid, ids,context=context):
            for line in move.move_lines:
                total += line.executed 
            res[move.id]= total 
        return res
    
    def _compute_compromised(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        total=0.0
        for move in self.browse(cr, uid, ids,context=context):
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
        for move in self.browse(cr ,uid, ids, context=context):
            for line in move.move_lines:
                mov_line_obj.write(cr, uid, line.id, {'date' : line.date}, context=context)
            self.write(cr, uid, ids, {'code':move.code}, context=context) 
    
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
     
    _columns = {
        'code': fields.char('Code', size=64, ),
        'origin': fields.char('Origin', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'program_line_id': fields.many2one('budget.program.line', 'Program line', readonly=True, states={'draft':[('readonly',False)]},),
        'date': fields.datetime('Date created', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection(STATE_SELECTION, 'State', readonly=True, 
        help="The state of the move. A move that is still under planning is in a 'Draft' state. Then the move goes to 'Reserved' state in order to reserve the designated amount. This move goes to 'Compromised' state when the purchase operation is confirmed. Finally goes to the 'Executed' state where the amount is finally discounted from the budget available amount", select=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'fixed_amount' : fields.float('Fixed amount', digits_compute=dp.get_precision('Account'),),
        'standalone_move' : fields.boolean('Standalone move', readonly=True, states={'draft':[('readonly',False)]} ),
        'arch_reserved':fields.float('Original Reserved', digits_compute=dp.get_precision('Account'),),
        'reserved': fields.function(_calc_reserved, type='float', method=True, string='Reserved',readonly=True, store=True),
        'reversed': fields.function(_calc_reversed, type='float', method=True, string='Reversed',readonly=True, store=True),
        'arch_compromised':fields.float('Original compromised',digits_compute=dp.get_precision('Account'),),
#TODO: to make it functional
        'compromised': fields.function(_compute_compromised, type='float', method=True, string='Compromised',readonly=True, store=True ),
        'executed': fields.function(_compute_executed, type='float', method=True, string='Executed',readonly=True, store=True ),
        'account_invoice_ids': fields.one2many('account.invoice', 'budget_move_id', 'Invoices' ),
        #'purchase_order_ids': fields.one2many('purchase.order', 'budget_move_id', 'Purchase orders' ),
        #'sale_order_ids': fields.one2many('sale.order', 'budget_move_id', 'Purchase orders' ),
        'move_lines': fields.one2many('budget.move.line', 'budget_move_id', 'Move lines' ),
        'type': fields.selection(_select_types, 'Move Type', required=True, readonly=True, states={'draft':[('readonly',False)]}),
    }
    _defaults = {
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'standalone_move':_check_manual
    }
    
    def _check_values(self, cr, uid, ids, context=None):
        list_line_ids_repeat = []
        
        for move in self.browse(cr, uid, ids, context=context):
            if  move.type in ('invoice_in','manual_invoice_in','expense','payroll','manual', 'opening','extension') and move.fixed_amount <= 0:
                return [False,_('The reserved amount must be positive')]
            if  move.type in ('invoice_out','manual_invoice_out') and move.fixed_amount >= 0:
                return [False,_('The reserved amount must be negative')]
            if  move.type in ('modifications') and move.fixed_amount != 0:
                return [False,_('The sum of addition and sustractions from program lines must be zero')]
            
            #Check if exist a repeat program_line
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
                elif line.type in ('opening','manual_invoice_in'):
                    if line.program_line_id.available_budget < line.fixed_amount:
                        return [False, _('The amount to substract from ') + line.program_line_id.name + _(' is greater than the available ')]
        return [True,'']
    
    def create(self, cr, uid, vals, context={}):
        if 'code' not in vals.keys():
            vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'budget.move')
        else:
            if vals['code']== None or vals['code'] == '':
                vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'budget.move')
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
                #self.write(cr, uid, [move.id], {'fixed_amount':res_amount}, context=context)
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
                obj_mov_line.write(cr, uid, [line.id],{'date':line.date }, context=context)
            self.write(cr, uid, [move.id], {'state': 'executed'})
        return True
#            
#    def action_cancel(self, cr, uid, ids, context=None):
#        self.write(cr, uid, ids, {'state': 'cancelled'})
#        return True
    
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
        for move in self.browse(cr, uid, ids,):
            if move.type in ('opening','extension','modification'):
                if move.state == 'in_execution':
                    return True
            if move.type in ('manual_invoice_in'):
                if move.executed == move.fixed_amount - move.reversed:
                    return True
        return False
    
    def is_in_execution(self, cr, uid, ids, *args):
        for move in self.browse(cr, uid, ids,):
            if move.type in ('opening','extension','modification'):
                    return False
            if move.type in ('manual_invoice_in'):
                if move.executed != move.fixed_amount - move.reversed:
                    return True
        return False
    
    def dummy_button(self,cr,uid, ids,context=None):
        return True   
    
    def unlink(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'draft':
                raise osv.except_osv(_('Error!'), _('Orders in state other than draft cannot be deleted \n'))
        super(budget_move,self).unlink(cr, uid, ids, context=context)


class budget_move_line(osv.osv):
    _name = "budget.move.line"
    _description = "Budget Move Line"
    
    def on_change_program_line(self, cr, uid, ids, program_line, context=None):
        for line in self.pool.get('budget.program.line').browse(cr, uid,[program_line], context=context):
            return {'value': {'line_available':line.available_budget},}
        return {'value': {}}
    
    def _compute(self, cr, uid, ids, field_names, args, context=None):
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
            if line.state in ('executed','in_execution'):
                if line.type == 'opening':
                    executed = line.fixed_amount
                    
                elif line.type == 'manual_invoice_in':
                    line_ids_bar = amld.search(cr, uid, [('target_budget_move_line_id','=', line.id),('account_move_line_type','=','liquid')], context=context)
                    for bar_line in amld.browse(cr, uid, line_ids_bar, context=context):
                        executed += bar_line.amount
            
            void_line_ids_amld = amld.search(cr, uid, [('target_budget_move_line_id','=', line.id),('account_move_line_type','=','void')], context=context)
            for void_line in amld.browse(cr, uid, void_line_ids_amld, context=context):
                reversed += void_line
                        
            if line.state in ('compromised','executed','in_execution'):
                compromised = line.fixed_amount - executed - line.reversed
            
            
            if line.state == 'reserved':
                    reserved = line.fixed_amount - reversed
                
            res[line.id]['executed'] = executed
            res[line.id]['compromised'] = compromised 
            res[line.id]['reversed'] = reversed
            res[line.id]['reserved'] = reserved 
        return res
    
#    
#    def _compute_reserved(self, cr, uid, ids, field_name, args, context=None):
#        res = {}
#        lines = self.browse(cr, uid, ids,context=context) 
#        for line in lines:
#            total = 0.0
#            if line.state == 'reserved':
#                    total = line.fixed_amount - line.reversed
#            res[line.id]= total 
#        return res
#    
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
        #'name': fields.related('budget_move_id', 'code', type='char', size=128, string = 'Budget Move Name'),
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
        #'expense_line_id': fields.many2one('hr.expense.line', 'Expense line', ),
        #'payslip_line_id': fields.many2one('hr.payslip.line', 'Payslip line', ),
        'move_line_id': fields.many2one('account.move.line', 'Move line', ),
        'account_move_id': fields.many2one('account.move', 'Account Move', ),
        'type': fields.related('budget_move_id', 'type', type='char', relation='budget.move', string='Type', readonly=True),
        'state': fields.related('budget_move_id', 'state', type='char', relation='budget.move', string='State',  readonly=True)
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'reversed': 0.0
        }
    
    _constraints=[
        (_check_plan_state, 'Error!\n The plan for this program line must be in approved state', ['fixed_amount','type']),
        ]
    
    def write(self, cr, uid, ids, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        super(budget_move_line, self).write(cr, uid, ids, vals, context=context)
#        for line in self.browse(cr, uid, ids, context=context):
#            move_id =line.budget_move_id.id
#            bud_move_obj.write(cr,uid, [move_id], {'date':line.budget_move_id.date},context=context)
        

#class budget_account_reconcile(osv.osv):
#    _name = "budget.account.reconcile"
#    _description = "Budget Account Reconcile"
#    
#    _columns = {
#         'budget_move_id': fields.many2one('budget.move', 'Budget Move', required=True, ),       
#         'budget_move_line_id': fields.many2one('budget.move.line', 'Budget Move Line', required=True, ),
#         'account_move_line_id': fields.many2one('account.move.line', 'Account Move Line', required=True, ),
#         'account_move_reconcile_id': fields.many2one('account.move.reconcile', 'Account Move Reconcile', required=True, ),
#         'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'), required=True),
#    }
#    
#    def clean_reconcile_entries(self, cr, uid, move_line_ids, context=None):
#        lines = []
#        for move_line_id in move_line_ids:
#            result = self.search(cr ,uid, [('account_move_line_id','=', move_line_id)], context=context)
#            lines += result
#        self.unlink(cr, uid, lines,context=context)
#        return True
    
class account_move_line_distribution(orm.Model):
    _name = "account.move.line.distribution"
    _description = "Account move line distribution"

    _columns = {         
         'account_move_line_id': fields.many2one('account.move.line', 'Account Move Line', required=True,),
         'distribution_percentage': fields.float('Distribution Percentage', required=True, digits_compute=dp.get_precision('Account'),),
         'distribution_amount': fields.float('Distribution Amount', digits_compute=dp.get_precision('Account'), required=True),
         'target_budget_move_line_id': fields.many2one('budget.move.line', 'Target Budget Move Line',),
         'target_account_move_line_id': fields.many2one('account.move.line', 'Target Budget Move Line'),
         'reconcile_ids': fields.many2many('account.move.reconcile','bud_reconcile_distribution_ids',),
         'type': fields.selection([('manual', 'Manual'),('auto', 'Automatic')], 'Distribution Type', select=True),
         'account_move_line_type': fields.selection([('liquid', 'Liquid'),('void', 'Void')], 'Account move line type', select=True),
    }
    
    _defaults = {
        'type': 'manual', 
        'distribution_amount': 0.0,
        'distribution_percentage': 0.0,
    }
    
    #A distribution line only has one target. This target can be a move_line or a budget_line
    def _check_target_move_line (self, cr, uid, ids, context=None):
        distribution_line_obj = self.browse(cr, uid, ids[0],context)
        
        if distribution_line_obj.target_budget_move_line_id and distribution_line_obj.target_account_move_line_id:
            return False
        else:
            return True
    
    _constraints = [
        (_check_target_move_line,'A Distribution Line only has one target. A target can be a move line or a budget move line',['target_budget_move_line_id', 'target_account_move_line_id']),
    ]

    def clean_reconcile_entries(self, cr, uid, move_line_ids, context=None):
        lines = []
        for move_line_id in move_line_ids:
            result = self.search(cr ,uid, [('account_move_line_id','=', move_line_id)], context=context)
            lines += result
        self.unlink(cr, uid, lines,context=context)
        return True
