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
from copy import copy
from openerp.tools.translate import _

class CashDistributionError(osv.except_osv):
    name =""
    value = ""
    move_id=0 
    def __init__(self, name, value, move_id):
        self.value = name
        self.value = value
        self.move_id =move_id
        osv.except_osv.__init__(self, name, value)

        osv.except_osv
        
class accountReconcileinherit(orm.Model):
    
    _inherit = "account.move.reconcile"
    
    """
    #Inherit create of account.move.reconcile
    def create(self, cr, uid, vals, context=None):
        account_move_obj= self.pool.get('account.move')
        is_incremental = self.check_incremental_reconcile(cr, uid, vals, context=context)
        reconcile_id = super(accountReconcileinherit, self).create(cr, uid, vals, context=context)
        try:
            self.reconcile_check_cash_flow(cr, uid, [reconcile_id], context=context, is_incremental=is_incremental) 
        except CashDistributionError, error:
            msg= _('Cash Flow distributions cannot be created automatically for this reconcile')
            account_move_obj.message_post(cr, uid, [error.move_id], body=msg, context=context)
        return reconcile_id
    
    #Delete all lines that match with reconcile
    def unlink(self, cr, uid, ids, context={}):
        dist_obj = self.pool.get('cash.flow.distribution')
        dist_ids = dist_obj.search(cr, uid, [('reconcile_ids.id','in',ids)], context=context)
        dist_obj.unlink(cr, uid, dist_ids, context=context)
        
        return super(accountReconcileinherit, self).unlink(cr, uid, ids, context=context)
    """
    
    #Get counterparts of a specific line.
    def _get_move_counterparts_cash_flow(self, cr, uid, line, context={}):
        is_debit = True if line.debit else False
        res = []
       
        for move_line in line.move_id.line_id:
            if (is_debit and move_line.credit) or (not is_debit and move_line.debit):
                res.append(move_line)
                
        return res
        
    def _recursive_liquid_get_auto_distribution_cash_flow(self, cr, uid, original_line, actual_line = None, checked_lines = [], amount_to_dist = 0.0, original_amount_to_dist = 0.0, reconcile_ids = [], continue_reconcile = False, context={}, is_incremental=False):
        
        dist_obj = self.pool.get('cash.flow.distribution')
        
        # Check if first call. Find line that moves cash
        if not actual_line and not original_line.account_id.moves_cash:
            return []
                
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
            counterparts = self._get_move_counterparts_cash_flow(cr, uid, actual_line, context=context)
        
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
                none_res += self._recursive_liquid_get_auto_distribution_cash_flow(cr, uid, original_line,
                                                                 actual_line = line,
                                                                 checked_lines = checked_lines,
                                                                 amount_to_dist = line_amount_to_dist,
                                                                 original_amount_to_dist = original_amount_to_dist,
                                                                 reconcile_ids = new_reconcile_ids,
                                                                 continue_reconcile = (not continue_reconcile),
                                                                 context = context)
        
        # Check if there is cash flow types or liquid lines, if not return none_res, even if its empty.
        cash_res = []
        liquid_res = []
        cash_distributed = 0.0
        liquid_distributed = 0.0
        
        if cash_lines or liquid_lines:
            # Write dist and build lists
            dist_obj = self.pool.get('cash.flow.distribution')
            
            #Cash list
            for line in cash_lines.values():
                distribution_amount = cash_amounts[line.id]
                if line.debit - line.credit < 0:
                    signed_dist_amount = distribution_amount * -1
                else:
                    signed_dist_amount = distribution_amount
                cash_distributed += distribution_amount
                vals = {
                    'account_move_line_id':         original_line.id,
                    'distribution_amount':          signed_dist_amount,
                    'distribution_percentage':      100 * abs(original_amount_to_dist) / abs(distribution_amount),
                    'target_account_move_line_id':  line.id,
                    'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                    'type':                         'move_cash_flow',
                }
                cash_res.append(dist_obj.create(cr, uid, vals, context = context))
            
            # Liquid list
            for line in liquid_lines.values():
                distribution_amount = liquid_amounts[line.id]
                if line.debit - line.credit < 0: 
                    signed_dist_amount = distribution_amount * -1
                else:
                    signed_dist_amount = distribution_amount
                liquid_distributed += distribution_amount
                vals = {
                    'account_move_line_id':         original_line.id,
                    'distribution_amount':          signed_dist_amount,
                    'distribution_percentage':      100 * abs(original_amount_to_dist) / abs(distribution_amount),
                    'target_account_move_line_id':  line.id,
                    'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                    'type':                         'type_cash_flow',
                }
                liquid_res.append(dist_obj.create(cr, uid, vals, context = context))
            
        distributed_amount = cash_distributed + liquid_distributed
        
        # Check if some dists are returned to adjust their values
        if none_res:
            self._adjust_distributed_values(cr, uid, none_res, amount_to_dist - distributed_amount, context = context, object="cash_flow")
        
        return cash_res + liquid_res + none_res
    
    def reconcile_check_cash_flow(self, cr, uid, ids, context={},is_incremental=False):
        done_lines = []

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
                    dist_ids = self._recursive_liquid_get_auto_distribution_cash_flow(cr, uid, line, context=context)
                    checked_dist_ids = self._check_auto_distributions(cr, uid, line, dist_ids, context=context, object="cash_flow")
                  
                elif (line.id not in done_lines) and line.account_id and line.account_id.cash_flow_type:
                    dist_ids = self._recursive_liquid_get_auto_distribution_cash_flow(cr, uid, line, context=context)
                    checked_dist_ids = self._check_auto_distributions(cr, uid, line, dist_ids, context=context, object="cash_flow")
 
                done_lines.append(line.id)

        return res