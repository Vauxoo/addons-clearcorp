# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.osv import fields, orm, osv
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from copy import copy

class CashBudgetDistributionError(osv.except_osv):
    name =""
    value = ""
    move_id=0 
    def __init__(self, name, value, move_id):
        self.value = name
        self.value = value
        self.move_id =move_id
        osv.except_osv.__init__(self, name, value)

        osv.except_osv
        
class AccountMoveReconcile(orm.Model):
    _inherit = 'account.move.reconcile'
    
    def unlink(self, cr, uid, ids, context={}):
        dist_obj = self.pool.get('account.move.line.distribution')
        bud_mov_obj = self.pool.get('cash.budget.move')
        dist_ids = dist_obj.search(cr, uid, [('reconcile_ids.id','in',ids)], context=context)
        dists = dist_obj.browse(cr, uid, dist_ids, context=context)
        budget_move_ids = []
        for dist in dists:
            if dist.target_budget_move_line_id and \
                dist.target_budget_move_line_id.budget_move_id and \
                dist.target_budget_move_line_id.budget_move_id.id not in budget_move_ids:
                budget_move_ids.append(dist.target_budget_move_line_id.budget_move_id.id)
        dist_obj.unlink(cr, uid, dist_ids, context=context)
        
        if budget_move_ids:
            bud_mov_obj.recalculate_values(cr, uid, budget_move_ids, context=context)
            for mov_id in budget_move_ids:
                bud_mov_obj.signal_workflow(cr, uid, [mov_id], 'button_check_execution', context=context)
        return super(AccountMoveReconcile, self).unlink(cr, uid, ids, context=context)
     
    def create(self, cr, uid, vals, context=None):
        account_move_obj= self.pool.get('account.move')
        is_incremental = self.check_incremental_reconcile(cr, uid, vals, context=context)
        reconcile_id = super(AccountMoveReconcile, self).create(cr, uid, vals, context=context)
        try:
            self.reconcile_budget_check(cr, uid, [reconcile_id], context=context, is_incremental=is_incremental) 
        except CashBudgetDistributionError, error:
            msg= _('Budget distributions cannot be created automatically for this reconcile')
            account_move_obj.message_post(cr, uid, [error.move_id], body=msg, context=context)
        return reconcile_id
    
    def move_in_voucher(self,cr, uid, move_ids, context=None):
        #Checks if a move is in a voucher, returns the id of the voucher or -1 in case that is not in any
        acc_move_obj = self.pool.get('account.move')
        acc_vouch_obj = self.pool.get('account.voucher')
        for move_id in move_ids:
            voucher_search = acc_vouch_obj.search(cr, uid, [('move_id','=',move_id)], context=context)
            if len(voucher_search) > 0:
                return voucher_search[0]
            else:
                return -1
    
    def move_in_invoice(self,cr, uid, move_ids, context=None):
        #checks if a move is in an invoice, returns the id of the invoice or -1 in case that is not in any
        acc_move_obj = self.pool.get('account.move')
        acc_inv_obj = self.pool.get('account.invoice')
        for move_id in move_ids:
            invoice_search = acc_inv_obj.search(cr, uid, [('move_id','=',move_id)], context=context)
            if len(invoice_search) > 0:
                return invoice_search[0]
            else:
                return -1
    
    def line_in_move(self,cr, uid, line_ids, context=None):
        #checks if a move is in an invoice, returns the id of the invoice or -1 in case that is not in any
        mov_line_obj = self.pool.get('account.move.line')
        for line in mov_line_obj.browse(cr, uid, line_ids, context=context):
            return line.move_id.id
        return -1
    
    def create_budget_account_reconcile(self, cr, uid, invoice_id, payment_move_line_id, payment_reconcile_id, reconcile_ids, context=None):
        acc_inv_obj = self.pool.get('account.invoice')
        acc_vouch_obj = self.pool.get('account.voucher')
        move_line_obj = self.pool.get('account.move.line')
        amld = self.pool.get('account.move.line.distribution')
        bud_move_obj = self.pool.get('cash.budget.move')
        bud_move_line_obj = self.pool.get('cash.budget.move.line')
        
        currency_id = None
        amount = 0
        for line in move_line_obj.browse(cr, uid, [payment_move_line_id],context=context):
            if line.credit > 0:
                amount = line.credit
            elif line.debit > 0:
                amount = line.debit
            elif line.debit == 0 and line.credit == 0:
                amount = line.amount_currency
                currency_id = line.currency_id
        if currency_id:
            pass
            #TODO
            #Distributions work only with system currency, if it is necessary to work with other currency, logic MUST be implemented from recursive distribution algorithms first        
        invoice = acc_inv_obj.browse(cr, uid,[invoice_id],context = context)[0]
        
        bud_move = invoice.budget_move_id
        i=0
        sum = 0
        for line in bud_move.move_lines:
            if i < len(bud_move.move_lines)-1:
                perc = line.fixed_amount/bud_move.fixed_amount or 0
                amld.create(cr, uid, {'budget_move_id': bud_move.id,
                                         'budget_move_line_id': line.id,
                                         'account_move_line_id': payment_move_line_id,
                                         'account_move_reconcile_id': payment_reconcile_id,
                                         'amount' : amount * perc
                                         })
                sum += amount * perc
                i+=1
                
            amld.create(cr, uid, {'budget_move_id': bud_move.id,
                                         'budget_move_line_id': bud_move.move_lines[i].id,
                                         'account_move_line_id': payment_move_line_id,
                                         'account_move_reconcile_id': payment_reconcile_id,
                                         'amount' : amount - sum
                                         })
            bud_move_line_obj.write(cr, uid, [line.id],{'date': line.date}, context=context)
        bud_move_obj.write(cr, uid , [bud_move.id], {'code': bud_move.code}, context=context)
    
    def _get_move_counterparts(self, cr, uid, line, context={}):
        is_debit = True if line.debit else False
        res = []
        debit_bud= False
        credit_bud=False
        
        for move_line in line.move_id.line_id:
            if move_line.credit and move_line.budget_program_line:
                credit_bud = True
            if move_line.debit and move_line.budget_program_line:
                debit_bud = True
        if credit_bud and debit_bud:
            raise CashBudgetDistributionError(_('Error'), _('Budget distributions cannot be created automatically for this reconcile'), line.move_id.id)
        
        for move_line in line.move_id.line_id:
            if (is_debit and move_line.credit) or (not is_debit and move_line.debit):
                res.append(move_line)
        return res
     
    def _recursive_liquid_get_auto_distribution(self, cr, uid, original_line, actual_line = None, checked_lines = [], amount_to_dist = 0.0, original_amount_to_dist = 0.0, reconcile_ids = [], continue_reconcile = False, context={},is_incremental=False):
        """
        Receives an account.move.line that moves liquid and was found creating a reconcile.
        This method starts at this line and "travels" through the moves and reconciles line counterparts
        to try to find a budget move to match with.
        Returns the list of account.move.line.distribution created, or an empty list.
        """
        precision = self.pool[
            'decimal.precision'].precision_get(cr, uid, 'Account')
        dist_obj = self.pool.get('account.move.line.distribution')
        budget_move_line_obj = self.pool.get('cash.budget.move.line')
        
        # Check if not first call and void type line. This kind of lines only can be navigated when called first by the main method.
        if actual_line and actual_line.move_id.budget_type == 'void':
            return []
        
        # Check if first call and not liquid or void line
        if not actual_line and not original_line.account_id.moves_cash:
            return []
        
        # Check for first call
        if not actual_line:
            dist_search = dist_obj.search(cr, uid, [('account_move_line_id','=',original_line.id)],context=context)
            dist_obj.unlink(cr,uid,dist_search,context=context,is_incremental=is_incremental)
            actual_line = original_line
            amount_to_dist = original_line.debit + original_line.credit
            original_amount_to_dist = amount_to_dist
            checked_lines = [actual_line.id]
        
        if not amount_to_dist:
            return []
        
        budget_lines = {}
        liquid_lines = {}
        none_lines = {}
        
        budget_amounts = {}
        liquid_amounts = {}
        
        budget_total = 0.0
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
                # Check if there are any budget move lines associated with this counterpart
                budget_move_lines_found = budget_move_line_obj.search(cr, uid, [('move_line_id','=',counterpart.id)], context=context)
                if budget_move_lines_found:
                    budget_lines[counterpart.id] = budget_move_lines_found
                    budget_amounts[counterpart.id] = counterpart.debit + counterpart.credit
                    budget_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
                elif counterpart.account_id.moves_cash:
                    liquid_lines[counterpart.id] = counterpart
                    liquid_amounts[counterpart.id] = counterpart.debit + counterpart.credit
                    liquid_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
                    checked_lines.append(counterpart.id)
                else:
                    none_lines[counterpart.id] = counterpart
                    none_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
                    checked_lines.append(counterpart.id)
        
        if not (budget_lines or liquid_lines or none_lines):
            return []
        
        if amount_total and amount_total > amount_to_dist:
            budget_amount_to_dist = float_round(
                budget_total * amount_to_dist / amount_total,
                precision_digits=precision)
            liquid_amount_to_dist = float_round(
                liquid_total * amount_to_dist / amount_total,
                precision_digits=precision)
            none_amount_to_dist = amount_to_dist - budget_amount_to_dist - \
                liquid_amount_to_dist
        elif amount_total:
            budget_amount_to_dist = budget_total
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
                none_res += self._recursive_liquid_get_auto_distribution(cr, uid, original_line,
                                                                 actual_line = line,
                                                                 checked_lines = checked_lines,
                                                                 amount_to_dist = line_amount_to_dist,
                                                                 original_amount_to_dist = original_amount_to_dist,
                                                                 reconcile_ids = new_reconcile_ids,
                                                                 continue_reconcile = (not continue_reconcile),
                                                                 context = context)
        
        # Check if there is budget, void or liquid lines, if not return none_res, even if its empty.
        budget_res = []
        liquid_res = []
        budget_distributed = 0.0
        liquid_distributed = 0.0
        bud_move_obj = self.pool.get('cash.budget.move')
        if budget_lines or liquid_lines:
            # Write dists and build lists
            
            dist_obj = self.pool.get('account.move.line.distribution')
            
            # Budget list
            budget_total = 0.0
            budget_to_distribute = 0.0
            budget_budget_move_lines_ids = []
            budget_budget_move_lines = []
            #lines is an int (id)
            for lines in budget_lines.values():
                budget_budget_move_lines_ids += lines
            #Browse record: lines is an int not an object! 
            budget_budget_move_lines = self.pool.get('cash.budget.move.line').browse(cr,uid, budget_budget_move_lines_ids,context=context)
            for line in budget_budget_move_lines:
                budget_total += abs(line.fixed_amount)
                budget_to_distribute += abs(line.fixed_amount) - \
                    abs(line.executed)

            signed_dist_amount_total = 0.0
            dist_percentage_total = 0.0

            vals = {}
            amounts = {}
            for line in budget_budget_move_lines:
                if line.executed != line.fixed_amount:
                    distribution_amount = abs(line.fixed_amount)

                    # If the resulting total of budget plus liquid lines is more than available, the amount has to be fractioned.
                    if abs(budget_total) > budget_amount_to_dist:
                        distribution_amount = float_round(
                            distribution_amount * budget_amount_to_dist / \
                            budget_total, precision_digits=precision)

                    if line.fixed_amount < 0:
                        signed_dist_amount = distribution_amount * -1
                    else:
                        signed_dist_amount = distribution_amount

                    dist_percentage = float_round(
                        100 * abs(distribution_amount) / \
                            abs(original_amount_to_dist),
                        precision_digits=2)

                    budget_distributed += distribution_amount
                    signed_dist_amount_total += signed_dist_amount

                    dist_percentage_total += dist_percentage
                    vals[line.id] = {
                        'account_move_line_id':         original_line.id,
                        'distribution_amount':          signed_dist_amount,
                        'distribution_percentage':      dist_percentage,
                        'target_budget_move_line_id':   line.id,
                        'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                        'type':                         'auto',
                        'account_move_line_type':       'liquid',
                    }
                    amounts[line.id] = {
                    }
                    budget_res.append(dist_obj.create(cr, uid, vals[line.id], context = context))

                    bud_move_obj.signal_workflow(cr, uid, [line.budget_move_id.id], 'button_check_execution', context=context)

            if signed_dist_amount_total != budget_amount_to_dist or \
                    dist_percentage_total != 100.0:
                pass

            # Liquid list
            for line in liquid_lines.values():
                distribution_amount = liquid_amounts[line.id]
                if line.debit - line.credit > 0:
                    signed_dist_amount = distribution_amount * -1
                else:
                    signed_dist_amount = distribution_amount
                liquid_distributed += distribution_amount
                vals = {
                    'account_move_line_id':         original_line.id,
                    'distribution_amount':          signed_dist_amount,
                    'distribution_percentage':      100 * abs(distribution_amount) / abs(original_amount_to_dist),
                    'target_account_move_line_id':  line.id,
                    'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                    'type':                         'auto',
                }
                liquid_res.append(dist_obj.create(cr, uid, vals, context = context))
                bud_move_obj.signal_workflow(cr, uid, [line.budget_move_id.id], 'button_check_execution', context=context)
            
        distributed_amount = budget_distributed + liquid_distributed
        
        # Check if some dists are returned to adjust their values
        if none_res:
            self._adjust_distributed_values(cr, uid, none_res, amount_to_dist - distributed_amount, context = context, object="budget")
        
        return budget_res + liquid_res + none_res
    
    def _recursive_void_get_auto_distribution(self, cr, uid, original_line, actual_line = None, checked_lines = [], amount_to_dist = 0.0, original_amount_to_dist = 0.0, reconcile_ids = [], continue_reconcile = False, context={}):
        """
        Receives an account.move.line that is marked as void for budget moves and was found creating a reconcile.
        This method starts at this line and "travels" through the moves and reconciles line counterparts
        to try to find a budget move to match with.
        Returns the list of account.move.line.distribution created, or an empty list.
        """
        
        budget_move_line_obj = self.pool.get('cash.budget.move.line')
        
        # Check if not first call and void type line. This kind of lines only can be navigated when called first by the main method.
        if actual_line and actual_line.move_id != original_line.move_id and actual_line.move_id.budget_type == 'void':
            return []
        
        # Check if first call and not void line
        if not actual_line and not original_line.move_id.budget_type == 'void':
            return []
        
        # Check for first call
        if not actual_line:
            actual_line = original_line
            amount_to_dist = original_line.debit + original_line.credit
            original_amount_to_dist = amount_to_dist
            checked_lines = [actual_line.id]
        
        if not amount_to_dist:
            return []
        
        budget_lines = {}
        none_lines = {}
        
        budget_amounts = {}
        
        budget_total = 0.0
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
                # Check if there are any budget move lines associated with this counterpart
                budget_move_lines_found = budget_move_line_obj.search(cr, uid, [('move_line_id','=',counterpart.id)], context=context)
                if budget_move_lines_found:
                    budget_lines[counterpart.id] = budget_move_lines_found
                    budget_amounts[counterpart.id] = counterpart.debit + counterpart.credit
                    budget_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
                elif not counterpart.account_id.moves_cash and (counterpart.move_id == original_line.move_id or counterpart.move_id.budget_type != 'void'):
                    none_lines[counterpart.id] = counterpart
                    none_total += counterpart.debit + counterpart.credit
                    amount_total += counterpart.debit + counterpart.credit
            checked_lines.append(counterpart.id)
        
        if not (budget_lines or none_lines):
            return []
        
        if amount_total and amount_total > amount_to_dist:
            budget_amount_to_dist = budget_total * amount_to_dist / amount_total
            none_amount_to_dist = amount_to_dist - budget_amount_to_dist
        elif amount_total:
            budget_amount_to_dist = budget_total
            none_amount_to_dist = none_total
        else:
            # Nothing to distribute
            return []
        
        none_res = []
        if none_total:
            for line in none_lines.values():
                line_amount_to_dist = (none_amount_to_dist if line.debit + line.credit >= none_amount_to_dist else line.debit + line.credit)
                # Use none_amount_to_dist with all lines as we don't know which ones will find something
                none_res += self._recursive_void_get_auto_distribution(
                    cr, uid, original_line, actual_line=line,
                    checked_lines=checked_lines,
                    amount_to_dist=line_amount_to_dist,
                    reconcile_ids=new_reconcile_ids,
                    continue_reconcile=(not continue_reconcile),
                    original_amount_to_dist=original_amount_to_dist,
                    context=context)
        
        budget_res = []
        budget_distributed = 0.0
        # Check if there is budget, void or liquid lines, if not return none_res, even if its empty.
        if budget_lines:
            # Write dists and build lists
            
            dist_obj = self.pool.get('account.move.line.distribution')
            
            # Budget list
            budget_total = 0.0
            budget_budget_move_line_ids = []
            budget_budget_move_lines = []
            bud_move_obj = self.pool.get('cash.budget.move')
            bud_move_line_obj = self.pool.get('cash.budget.move.line')
            for lines in budget_lines.values():
                budget_budget_move_lines += lines
            for line in bud_move_line_obj.browse(cr, uid, budget_budget_move_lines, context=context):
                budget_budget_move_line_ids.append(line.id)
                budget_total +=  abs(line.compromised)
            for line in bud_move_line_obj.browse(cr, uid, budget_budget_move_lines, context=context):
                distribution_amount =  abs(line.compromised)
                # If the resulting total of budget plus liquid lines is more than available, the amount has to be fractioned.
                if budget_total > amount_to_dist:
                    distribution_amount = distribution_amount * amount_to_dist / budget_total
                if line.fixed_amount < 0:
                    signed_dist_amount = distribution_amount * -1
                else:
                    signed_dist_amount = distribution_amount
                budget_distributed += distribution_amount
                vals = {
                    'account_move_line_id':         original_line.id,
                    'distribution_amount':          signed_dist_amount,
                    'distribution_percentage':      100 * abs(distribution_amount) / abs(original_amount_to_dist),
                    'target_budget_move_line_id':   line.id,
                    'reconcile_ids':                [(6, 0, new_reconcile_ids)],
                    'type':                         'auto',
                    'account_move_line_type':       'void',
                }
                budget_res.append(dist_obj.create(cr, uid, vals, context = context))
                bud_move_obj.signal_workflow(cr, uid, [line.budget_move_id.id], 'button_check_execution', context=context)
        
        distributed_amount = budget_distributed
        
        # Check if some dists are returned to adjust their values
        if none_res:
            self._adjust_distributed_values(cr, uid, none_res, amount_to_dist - distributed_amount, context = context, object="budget")
        
        return budget_res + none_res
    
    def reconcile_budget_check(self, cr, uid, ids, context={}, is_incremental=False):
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
            # Check if the account if marked as moves_cash
            for line in move_lines:
                if (line.id not in done_lines) and line.account_id and line.account_id.moves_cash:
                    dist_ids = self._recursive_liquid_get_auto_distribution(cr, uid, line, context=context, is_incremental=is_incremental)
                    checked_dist_ids = self._check_auto_distributions(cr, uid, line, dist_ids, context=context,object="budget")
                    if checked_dist_ids:
                        res[line.id] = checked_dist_ids
                elif (line.id not in done_lines) and line.move_id.budget_type == 'void':
                    dist_ids = self._recursive_void_get_auto_distribution(cr, uid, line, context=context)
                    checked_dist_ids = self._check_auto_distributions(cr, uid, line, dist_ids, context=context, object="budget")
                    if checked_dist_ids:
                        res[line.id] = checked_dist_ids
                done_lines.append(line.id)
            
            # Recalculate budget move values
            if res:
                budget_move_ids = []
                dist_obj = self.pool.get('account.move.line.distribution')
                dist_ids = [dist_id for dist_ids in res.values() for dist_id in dist_ids]
                dists = dist_obj.browse(cr, uid, dist_ids)
                for dist in dists:
                    if dist.target_budget_move_line_id and dist.target_budget_move_line_id.budget_move_id:
                        budget_move_ids.append(dist.target_budget_move_line_id.budget_move_id.id)
                if budget_move_ids:
                    budget_move_obj = self.pool.get('cash.budget.move')
                    budget_move_obj.recalculate_values(cr, uid, budget_move_ids, context = context)
        return res 

class Account(osv.Model):
    _inherit = 'account.account'
    
    _columns = {
        'default_budget_program_line' : fields.many2one('cash.budget.program.line','Default budget program line'),
    }
