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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

class AccountMoveReconcile(orm.Model):
    _inherit = 'account.move.reconcile'
    
    """
        This class is a base for cash flow distribution (Cash Flow Report) and
        account move line distribution (Budget). In this class exists functions
        that they have in common and their are used for both models.
    """
    
    def check_incremental_reconcile(self, cr, uid, vals, context=None):
        #Checks for every account move line, that if the AML(account move line) has a reconcile (partial or complete), each AML of the given reconcile must be e included in the new reconcile.
        acc_move_line_obj=self.pool.get('account.move.line')
        acc_move_line_tuples=[]
        acc_move_line_ids=[]
        previous_reconciles = []
        
        if vals.get('line_id', False):
            acc_move_line_tuples=vals.get('line_id', False)
        if vals.get('line_partial_ids', False):
            acc_move_line_tuples=vals.get('line_partial_ids', False)

        for tuple in acc_move_line_tuples:
            if tuple[0]== 4:
                acc_move_line_ids.append(tuple[1])

        for acc_move_line in acc_move_line_obj.browse(cr, uid, acc_move_line_ids, context=context):
             previous_reconcile = acc_move_line.reconcile_id
             previous_partial_reconcile = acc_move_line.reconcile_partial_id
             
             if previous_reconcile:
                 for aml in previous_reconcile.line_id:
                     if aml.id not in acc_move_line_ids:
                         return False
             elif previous_partial_reconcile:
                 for aml in previous_partial_reconcile.line_partial_ids:
                     if aml.id not in acc_move_line_ids:
                         return False
        return True
    
    def split_debit_credit(self,cr, uid, move_line_ids,context=None):
        #takes a list of given account move lines and classifies them in credit or debit
        #returns a dictionary with two keys('debit' and 'credit') and for values lists of account move line ids
        result ={}
        credit = []
        debit = []
        acc_move_line = self.pool.get('account.move.line')
        for line in acc_move_line.browse(cr, uid, move_line_ids,context=context):
            if line.credit > 0:
                credit.append(line.id)
            elif line.debit > 0:
                debit.append(line.id)
            elif line.debit == 0 and line.credit == 0:
                if line.amount_currency > 0:
                    debit.append(line.id)
                else:
                    credit.append(line.id)
        result ['debit'] = debit
        result ['credit'] = credit
        return result
    
    def _get_reconcile_counterparts(self, cr, uid, line, context={}):
        is_debit = True if line.debit else False
        reconcile_ids = []
        
        if line.reconcile_id:
            reconcile_lines = line.reconcile_id.line_id if line.reconcile_id and line.reconcile_id.line_id else []
            reconcile_ids.append(line.reconcile_id.id)
        elif line.reconcile_partial_id:
            reconcile_lines = line.reconcile_partial_id.line_partial_ids if line.reconcile_partial_id and line.reconcile_partial_id.line_partial_ids else []
            reconcile_ids.append(line.reconcile_partial_id.id)
        else:
            reconcile_lines = []
        
        res = []
        if reconcile_lines:
            for move_line in reconcile_lines:
                if (is_debit and move_line.credit) or (not is_debit and move_line.debit):
                    res.append(move_line)
        return reconcile_ids, res    
    
    """
        Pass a new parameter, object. It will help to identify which object is 
        used at moment and create the correct model. This parameter is necessary
        to avoid duplicate code in both models. 
        @param object: A string with model's name 
    """
    def _adjust_distributed_values(self, cr, uid, dist_ids, amount, context = {}, object=""):
        if object == "cash_flow":
            dist_obj = self.pool.get('cash.flow.distribution')
        elif object == "budget":
            dist_obj = self.pool.get('account.move.line.distribution')
        else:
            return False
        
        distributed_amount = 0.0
        dists = dist_obj.browse(cr, uid, dist_ids, context = context)
        
        if amount <= 0.0:
            dist_obj.unlink(cr, uid, dist_ids, context = context)
            return True
        
        for dist in dists:
            distributed_amount += dist.distribution_amount
        if distributed_amount and distributed_amount > amount:
            for dist in dists:
                vals = {
                    'distribution_percentage':dist.distribution_percentage * amount / distributed_amount,
                    'distribution_amount':dist.distribution_amount * amount / distributed_amount,
                }
                dist_obj.write(cr, uid, [dist.id], vals, context = context)
            return True
        return False
    
    """
        Pass a new parameter, object. It will help to identify which object is 
        used at moment and create the correct model. This parameter is necessary
        to avoid duplicate code in both models. 
        @param object: A string with model's name 
    """
    def _check_auto_distributions(self, cr, uid, line, dist_ids, context = {}, object=""):
        
        # Check for exact value computation
        if line and dist_ids:
            if object == "cash_flow":
                dist_obj = self.pool.get('cash.flow.distribution')
            elif object == "budget":
                dist_obj = self.pool.get('account.move.line.distribution')
                        
            dists = dist_obj.browse(cr, uid, dist_ids, context = context)
            distribution_amount = 0.0            
            distribution_percentage = 0.0
            #Check amounts for a particular line
            for dist in dists:
                distribution_amount += dist.distribution_amount
                distribution_percentage += dist.distribution_percentage            
            last_dist = dists[-1]
            last_dist_distribution_amount = last_dist.distribution_amount
            last_dist_distribution_percentage = last_dist.distribution_percentage
            amount = line.debit + line.credit
            
            vals = {}
            if abs(distribution_amount) > amount:
                if (abs(distribution_amount) - amount) > abs(last_dist_distribution_amount):
                    # Bad dists, the difference is bigger than the adjustment line (last line)
                    dist_obj.unlink(cr, uid, dist_ids, context=context)
                    return []
                else:
                    # Adjust difference
                    if distribution_amount > 0:
                        vals['distribution_amount'] = amount - (abs(distribution_amount) - abs(last_dist_distribution_amount))
                    else:
                        vals['distribution_amount'] = -(amount - (abs(distribution_amount) - abs(last_dist_distribution_amount)))
                        
            elif distribution_amount < amount:
                if distribution_amount > 0:
                    vals['distribution_amount'] = amount - (abs(distribution_amount) - abs(last_dist_distribution_amount))
                else:
                    vals['distribution_amount'] = -(amount - (abs(distribution_amount) - abs(last_dist_distribution_amount)))
                    
            if 'distribution_amount' in vals:
                if last_dist.target_account_move_line_id and \
                    abs(vals['distribution_amount']) > (last_dist.target_account_move_line_id.debit + last_dist.target_account_move_line_id.credit):
                    # New value is bigger than allowed value
                    dist_obj.unlink(cr, uid, dist_ids, context=context)
                    return []
                
                #Create this "exception", because only with budget model review
                #target_budget_move_line_id field.
                elif object == "budget":
                    if last_dist.target_budget_move_line_id and \
                        abs(distribution_amount) > abs(last_dist.target_budget_move_line_id.fixed_amount):
                        # New value is bigger than allowed value
                        dist_obj.unlink(cr, uid, dist_ids, context=context)
                        return []
            
            if distribution_percentage > 100:
                if (distribution_percentage - 100) > last_dist_distribution_percentage:
                    # Bad dists, the difference is bigger than the adjustment line (last line)
                    dist_obj.unlink(cr, uid, dist_ids, context=context)
                    return []
                else:
                    # Adjust difference
                    vals['distribution_percentage'] = 100 - (distribution_percentage - last_dist_distribution_percentage)
            
            elif distribution_percentage < 100:
                vals['distribution_percentage'] = 100 - (distribution_percentage - last_dist_distribution_percentage)

            dist_obj.write(cr, uid, [last_dist.id], vals, context=context)
            return dist_ids