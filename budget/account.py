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
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
from datetime import datetime

class account_move_reconcile(osv.osv):
    _inherit = 'account.move.reconcile'
    
    
    
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
                if amount_currency > 0:
                    debit.append(line.id)
                else:
                    credit.append(line.id)
        result ['debit'] = debit
        result ['credit'] = credit
        return result
    
    def get_counterparts(self, cr, uid, move_line_id, classified_lines, context=None):
        #to be used with the result of method "split_debit_credit" returns the counterparts of a given account move line  
        if move_line_id in classified_lines['debit']:
            return classified_lines['credit']
        else:
            return classified_lines['debit']      

    def split_move_noncash(self,cr, uid, move_ids,context=None):
        #Classifies every move line of the account move in cash or non cash
        #for a move, returns a dictionary, with the id of the move line as the key and 'cash' or 'non_cash' for values
        result ={}
#        acc_move_line = self.pool.get('account.move.line')
        acc_move_obj = self.pool.get('account.move')
        for move in acc_move_obj.browse(cr, uid, move_ids, context=context):
            for line in move.line_id:
                if line.account_id.moves_cash:
                    result[line.id] = 'cash'
                else:
                    result[line.id] = 'non_cash'
            return result
    
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
               
            
    def create_budget_account_reconcile(cr, uid, invoice_id, payment_move_line_id, payment_reconcile_id, reconcile_ids, context=None):
        acc_inv_obj = self.pool.get('account.invoice')
        acc_vouch_obj = self.pool.get('account.voucher')
        move_line_obj = self.pool.get('account.move.line')
        bar_obj = self.pool.get('budget.account.reconcile')
        
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
           print 'TODO'
           #amount = how to get the equivalent in system currency?         
        invoice = acc_inv_obj.browse(cr, uid,[invoice_id],context = context)[0]
        
        bud_move = invoice.budget_move_id
        i=0
        sum = 0
        for line in bud_move.move_lines:
            if i < len(bud_move.move_lines)-1:
                perc = line.fixed_amount/bud_move.fixed_amount or 0
                bar_obj.create(cr, uid, {'budget_move_id': bud_move.id,
                                         'budget_move_line_id': line.id,
                                         'account_move_line_id': payment_move_line_id,
                                         'account_move_reconcile_id': payment_reconcile_id,
                                         'amount' : amount * perc
                                         })
                sum += amount * perc
                i+=1
                
            bar_obj.create(cr, uid, {'budget_move_id': bud_move.id,
                                         'budget_move_line_id': bud_move.move_lines[i].id,
                                         'account_move_line_id': payment_move_line_id,
                                         'account_move_reconcile_id': payment_reconcile_id,
                                         'amount' : amount - sum
                                         })
                
                
    def on_create_budget_check(self, cr, uid, ids, visited_reconciles,trace_reconciled_ids, passing_through, context=None):
        voucher_obj = self.pool.get('account.voucher')
        acc_move_obj = self.pool.get('account.move')
        voucher_present = False
        invoice_present = False
        
        for reconcile in self.browse(cr, uid, ids, context=context):
            local_trace_reconciled_ids = trace_reconciled_ids
            local_trace_reconciled_ids += reconcile.id
            local_visited_reconciles = visited_reconciles
            lines = []
            line_ids = []
            move_ids = []
            
            #choosing between partial or total reconcile
            if reconcile.line_id:
                lines = reconcile.line_id
            elif reconcile.line_partial_id:
                lines = reconcile.line_partial_id
            
            #getting move_line_ids from reconcile lines
            reconcile_line_ids =  map(lambda x: x.id, lines)
            #getting move_ids from reconcile lines
            move_ids = map(lambda x: x.move_id.id, lines)
            
            
            cash_moves = self.split_move_noncash(cr, uid, move_ids, context=context)
            
            if 'cash' in cash_moves.values() or passing_trough:
                for move in acc_move_obj.browse(self, cr, uid, move_ids, context=context):
                    if cash_moves[move.id] == 'cash':                                      #if it moves cash and
                        voucher_id = self.move_in_voucher(cr, uid, [move_id], context=context)
                        if voucher_id != -1:                                               #is a voucher
                            classified_reconciled_lines = self.split_debit_credit(cr, uid, reconcile_line_ids, context)
                            for line in move.line_id:
                                reconcile_id = line.reconcile_id or line.reconcile_partial_id
                                if reconcile_id in reconcile_line_ids:
                                    reconcile_counterpart_ids = self.get_counterparts(cr, uid, line.id, classified_reconciled_lines, context)
                                    for counter_id in reconcile_counterpart_ids:
                                         invoice_id = self.move_in_invoice(cr, uid, [counter_id], context=context)
                                         if invoice_id != -1:
                                             self.create_budget_account_reconcile(cr, uid, invoice_id, line.id, reconcile_id, local_trace_reconciled_ids, context=context)

                    
            
