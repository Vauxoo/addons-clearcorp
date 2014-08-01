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

from openerp.osv import fields, orm

class cashFlowdistribution(orm.Model):
    _name = "cash.flow.distribution"
    _inherit = "account.distribution.line"
    _description = "Cash Flow Distribution"
    
     #======== Check distribution percentage. Use distribution_percentage_sum in account.move.line to check 
    def _check_distribution_percentage_cash(self, cr, uid, ids, context=None):          
        
        for distribution in self.browse(cr, uid, ids, context=context):
            #distribution_percentage_sum compute all the percentages for a specific move line. 
            line_percentage = distribution.account_move_line_id.distribution_percentage_sum_cash or 0.0
            line_percentage_remaining = 100 - line_percentage
            
            if distribution.distribution_percentage > line_percentage_remaining:
                return False
            
            return True
        
    #========= Check distribution percentage. Use distribution_amount_sum in account.move.line to check 
    def _check_distribution_amount_cash(self, cr, uid, ids, context=None):          
        amount = 0.0
        
        for distribution in self.browse(cr, uid, ids, context=context):
            #==== distribution_amount_sum compute all the percentages for a specific move line. 
            line_amount_dis = distribution.account_move_line_id.distribution_amount_sum_cash or 0.0
            
            #=====Find amount for the move_line
            if distribution.account_move_line_id.credit > 0:
                amount = distribution.account_move_line_id.credit
            if distribution.account_move_line_id.debit > 0:
                amount = distribution.account_move_line_id.debit
                        
            #====Check which is the remaining between the amount line and sum of amount in distributions. 
            amount_remaining = amount - line_amount_dis
            
            if distribution.distribution_amount > amount_remaining:
                return False            
            
            return True
    _columns = {
        'reconcile_ids': fields.many2many('account.move.reconcile', 'cash_reconcile_distribution_ids', string='Cash Reconcile Distributions',),
        'type': fields.selection([('type_cash_flow', 'Type Cash Flow'),('move_cash_flow', 'Moves Cash Flow')], 'Distribution Cash Flow Type', select=True),                
    }
    
    _constraints = [
        #(_check_distribution_percentage_cash, 'The cash flow distribution percentage  can not be greater than sum of all percentage for the account move line selected', ['account_move_line_id']),    
        #(_check_distribution_amount_cash, 'The cash flow distribution amount can not be greater than maximum amount of remaining amount for account move line selected', ['distribution_amount']),    
    ]
    
    _defaults = {
        'type': 'move_cash_flow', 
        'distribution_amount': 0.0,
        'distribution_percentage': 0.0,
    }
    
    #Line is an object
    def get_amounts_distribution(self, cr, uid, line, lines_distribution_list):
        amount = 0.0
        amount_line = 0.0
        
        for distribution in lines_distribution_list:
            amount += distribution.distribution_amount
        
        #Amount line
        if line.debit > 0.0:
            amount_line = line.debit        
        else:
            amount_line = line.credit
        
        if amount == amount_line:
            return 0.0
        else:
            return abs (amount_line - amount) 