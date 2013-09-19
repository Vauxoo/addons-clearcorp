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

from osv import fields,orm
from copy import copy

class accountReconcileinherit(orm.Model):
    
    _inherit = "account.move.reconcile"
    
    #Inherit create of account.move.reconcile
    def create(self, cr, uid, vals, context=None):
        reconcile_id = super(accountReconcileinherit, self).create(cr, uid, vals, context=context)
        #Cash Flow.
        self.reconcile_check_cash_flow(cr, uid, [reconcile_id], context=context)
        
        return reconcile_id
    
    #Delete all lines that match with reconcile
    def unlink(self, cr, uid, ids, context={}):
        dist_obj = self.pool.get('account.cash.flow.distribution')
        dist_ids = dist_obj.search(cr, uid, [('reconcile_ids.id','in',ids)], context=context)
        dist_obj.unlink(cr, uid, dist_ids, context=context)
        
        return super(accountReconcileinherit, self).unlink(cr, uid, ids, context=context)
    
    #Get counterparts of a specific line.
    def _get_move_counterparts(self, cr, uid, line, context={}):
        is_debit = True if line.debit else False
        res = []
        for move_line in line.move_id.line_id:
            if (is_debit and move_line.credit) or (not is_debit and move_line.debit):
                res.append(move_line)
        return res
    
    #Get counterparts in reconcile for a specific line
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
    
    #Adjust cash_flow_types values in account.cash.flow.distribution.
    def _adjust_distributed_values_cash_flow(self, cr, uid, dist_ids, amount, context = {}):
        dist_obj = self.pool.get('account.cash.flow.distribution')
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
                    'distribution_amount':dist.distribution_amount * amount / distributed_amount,
                }
                dist_obj.write(cr, uid, [dist.id], vals, context = context)
            return True
        
        return False
    
    def _distribution_move_lines_cash_flow(self, cr, uid, original_line, actual_line = None, checked_lines = [], amount_to_dist = 0.0, original_amount_to_dist = 0.0, reconcile_ids = [], continue_reconcile = False, context={}):
        
        """
            Receives an account.move.line that moves liquid and was found creating a reconcile.
            This method starts at this line and "travels" through the moves and reconciles line counterparts
            to try to find a budget move to match with.
            Returns the list of account.cash.flow.distribution created, or an empty list.
        """
                
        # Check for first call
        if not actual_line:
            actual_line = original_line
            amount_to_dist = original_line.debit + original_line.credit
            original_amount_to_dist = amount_to_dist
            checked_lines = [actual_line.id]
        
        if not amount_to_dist:
            return []
        
        cash_lines = {}
        liquid_lines = {}
        none_lines = {}
        
        cash_amounts = {}
        liquid_amounts = {}
        
        cash_total = 0.0
        liquid_total = 0.0
        none_total = 0.0
        
        amount_total = 0.0
        
        new_reconcile_ids = copy(reconcile_ids)
        
        # Get line counterparts, if the reconcile flag is on, the counterparts are looked in the reconcile, if not move is used
        if continue_reconcile:
            line_reconcile_ids, counterparts = self._get_reconcile_counterparts(cr, uid, actual_line, context=context)
            new_reconcile_ids += line_reconcile_ids
        else:
            counterparts = self._get_move_counterparts(cr, uid, actual_line, context=context)
        
        for counterpart in counterparts:
            if counterpart.id not in checked_lines: 
                #Lines has cash_flow_type 
                if counterpart.account_id.cash_flow_type:
                    cash_lines[counterpart.id] = counterpart
                    cash_amounts[counterpart.id] = counterpart.debit + counterpart.credit
                    cash_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
                
                #Lines has moves_cash checked -> liquid lines
                elif counterpart.account_id.moves_cash:
                    liquid_lines[counterpart.id] = counterpart
                    liquid_amounts[counterpart.id] = counterpart.debit + counterpart.credit
                    liquid_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
                    
                else:
                    none_lines[counterpart.id] = counterpart
                    none_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
            
            checked_lines.append(counterpart.id)
        
        if not (cash_lines or liquid_lines or none_lines):
            return []
        
        if amount_total and amount_total > amount_to_dist:
            cash_amount_to_dist = cash_total * amount_to_dist / amount_total
            liquid_amount_to_dist = liquid_total * amount_to_dist / amount_total
            none_amount_to_dist = amount_to_dist - cash_amount_to_dist - liquid_amount_to_dist
        
        elif amount_total:
            cash_amount_to_dist = cash_total
            liquid_amount_to_dist = liquid_total
            none_amount_to_dist = none_total
        
        else:
            # Nothing to distribute
            return []
        
        none_res = []
        if none_total:
            for line in none_lines.values():
                line_amount_to_dist = (none_amount_to_dist if line.debit + line.credit >= none_amount_to_dist else line.debit + line.credit)
                # Use none_amount_to_dist with all lines as we don't know which ones will find something
                none_res += self._distribution_move_lines_cash_flow(cr, uid, original_line,
                                                                 actual_line = line,
                                                                 checked_lines = checked_lines,
                                                                 amount_to_dist = line_amount_to_dist,
                                                                 original_amount_to_dist = original_amount_to_dist,
                                                                 reconcile_ids = new_reconcile_ids,
                                                                 continue_reconcile = (not continue_reconcile),
                                                                 context = context)
        
        # Check if there is budget, void or liquid lines, if not return none_res, even if its empty.
        cash_res = []
        liquid_res = []
        cash_distributed = 0.0
        liquid_distributed = 0.0
        
        if cash_lines or liquid_lines:
            # Write dists and build lists
            
            dist_obj = self.pool.get('account.cash.flow.distribution')
            
            #Cash list
            for line in cash_lines.values():
                distribution_amount = cash_amounts[line.id]
                cash_distributed += distribution_amount
                vals = {
                    'account_move_line_id':         original_line.id,
                    'distribution_amount':          distribution_amount,
                    'target_account_move_line':  line.id,
                    'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                }
                cash_res.append(dist_obj.create(cr, uid, vals, context = context))
            
            #Liquid list
            for line in liquid_lines.values():
                distribution_amount = liquid_amounts[line.id]
                liquid_distributed += distribution_amount
                vals = {
                    'account_move_line_id':         original_line.id,
                    'distribution_amount':          distribution_amount,
                    'target_account_move_line':  line.id,
                    'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                }
                liquid_res.append(dist_obj.create(cr, uid, vals, context = context))
            
        distributed_amount = cash_distributed + liquid_distributed
        
        # Check if some dists are returned to adjust their values
        if none_res:
            self._adjust_distributed_values_cash_flow(cr, uid, none_res, amount_to_dist - distributed_amount, context = context)
        
        return cash_res + liquid_res + none_res
    
    def _check_distributions_cash_flow(self, cr, uid, line, dist_ids, context = {}):
        # Check for exact value computation
        if line and dist_ids:
            dist_obj = self.pool.get('account.cash.flow.distribution')            
            dists = dist_obj.browse(cr, uid, dist_ids, context = context)
            distribution_amount = 0.0            
            #Check amounts for a particular line
            for dist in dists:
                distribution_amount += dist.distribution_amount            
            last_dist = dists[-1]
            last_dist_distribution_amount = last_dist.distribution_amount
            amount = line.debit + line.credit
            
            vals = {}
            if distribution_amount > amount:
                if (distribution_amount - amount) > last_dist_distribution_amount:
                    # Bad dists, the difference is bigger than the adjustment line (last line)
                    dist_obj.unlink(cr, uid, dist_ids, context=context)
                    return []
                else:
                    # Adjust difference
                    vals['distribution_amount'] = amount - (distribution_amount - last_dist_distribution_amount)
                    
            elif distribution_amount < amount:
                vals['distribution_amount'] = amount - (distribution_amount - last_dist_distribution_amount)
            
            if 'distribution_amount' in vals:
                if last_dist.target_account_move_line and \
                    vals['distribution_amount'] > (last_dist.target_account_move_line.debit + last_dist.target_account_move_line.credit):
                    # New value is bigger than allowed value
                    dist_obj.unlink(cr, uid, dist_ids, context=context)
                    return []               
               
            dist_obj.write(cr, uid, last_dist.id, vals, context=context)
            return dist_ids
    
    def reconcile_check_cash_flow(self, cr, uid, ids, context={}):
        done_lines = []
        res = {}
        
        for reconcile in self.browse(cr, uid, ids, context=context):
            # Check if reconcile "touches" a move that touches a liquid account on any of its move lines            
            # First get the moves of the reconciled lines
            if reconcile.line_id:
                moves = [line.move_id for line in reconcile.line_id]
            else:
                moves = [line.move_id for line in reconcile.line_partial_ids]
                
            # Then get all the lines of those moves, reconciled and counterparts
            move_lines = [line for move in moves for line in move.line_id]
            
            # Check if the account if marked as moves_cash and if account has a cash_flow_type
            for line in move_lines:
                if (line.id not in done_lines) and line.account_id and line.account_id.moves_cash:
                    dist_ids = self._distribution_move_lines_cash_flow(cr, uid, line, context=context)
                    checked_dist_ids = self._check_distributions_cash_flow(cr, uid, line, dist_ids, context=context)
                    if checked_dist_ids:
                        res[line.id] = checked_dist_ids
                
                elif (line.id not in done_lines) and line.account_id and line.account_id.cash_flow_type:
                    dist_ids = self._distribution_move_lines_cash_flow(cr, uid, line, context=context)
                    checked_dist_ids = self._check_distributions_cash_flow(cr, uid, line, dist_ids, context=context)
                    if checked_dist_ids:
                        res[line.id] = checked_dist_ids
                
                done_lines.append(line.id)

        return res