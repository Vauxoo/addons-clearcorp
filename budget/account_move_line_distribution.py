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

from tools.translate import _
from osv import fields, osv, orm

class account_move_line_distribution(orm.Model):
    _name = "account.move.line.distribution"
    _inherit = "account.distribution.line"
    _description = "Account move line distribution"

    _columns = {         
         'target_budget_move_line_id': fields.many2one('budget.move.line', 'Target Budget Move Line',),
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