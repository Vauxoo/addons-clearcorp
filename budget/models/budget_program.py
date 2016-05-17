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
                     'changed':'COALESCE(SUM(BML.changed),0.0) AS modified_amount',
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
   