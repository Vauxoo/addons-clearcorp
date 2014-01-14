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
import pooler
from report import report_sxw
from tools.translate import _
from openerp.osv import fields, osv, orm

from openerp.addons.account_report_lib.account_report_base import accountReportbase

class Parser(accountReportbase):
    
    def __init__(self, cr, uid, name, context):      
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'cr': cr,
            'uid':uid,
            'pool': pooler,
            'context': context,
            'get_data':self.get_data,
            
             #====================SET AND GET METHODS ===========================
            'storage':{},
            'set_data_template': self.set_data_template,
            #===================================================================
        })
    
    def set_data_template(self, cr, uid, data,context):
        
        cash_flow_amounts, cash_flow_types, total_by_type = self.get_data(cr, uid, data,context)
        
        dict_update = {
                       'cash_flow_amounts': cash_flow_amounts,
                       'cash_flow_types':cash_flow_types,
                       'total_by_type':total_by_type                       
                       }
        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #1. Report parameters
    def get_report_parameters(self, cr, uid, data, context):
        
        filter_data = [] #contains the start and stop period or dates.
 
        #===================FILTER PARAMETERS =====================#       
        fiscal_year = self.get_fiscalyear(data)        
        filter_type = self.get_filter(data)
        target_move = self.get_target_move(data)
        chart_account_id = self.get_chart_account_id(data)
        
        #======================FILTER TIME ===============================#       
        if filter_type == 'filter_period':            
            #Build filter_data
            filter_data.append(self.get_start_period(data))
            filter_data.append(self.get_end_period(data))
            
        elif filter_type == 'filter_date':
            #Build filter_data
            filter_data.append(start_date)
            filter_data.append(end_date)

        else:
            filter_type = ''        
        
        return {
                'filter_data' : filter_data,
                'filter_type': filter_type,
                'fiscal_year': fiscal_year,
                'chart_account_id': chart_account_id,
                'target_move': target_move,
                
                }
    
    #2. Get all accounts that moves_cash
    def get_accounts_moves_cash(self, cr, uid, context):
        return self.pool.get('account.account').search(cr, uid, [('moves_cash','=',True)])
    
    #3. Get move_lines that match with filters.
    def get_move_lines(self, cr, uid, data, context):
        
        account_report_lib = self.pool.get('account.webkit.report.library')
        account_dict = {}
        
        #======================================================
        #Accounts
        account_ids = self.get_accounts_moves_cash(cr, uid, context)        
        #Parameters
        parameter_dict = self.get_report_parameters(cr, uid, data, context)
        
        #Get move_lines for each account.
        for account_id in account_ids:
            if account_id not in account_dict.keys():
                account_dict[account_id] = account_report_lib.get_move_lines(cr, uid,
                                                       account_ids=account_ids,   
                                                       filter_type=parameter_dict['filter_type'], 
                                                       filter_data=parameter_dict['filter_data'], 
                                                       fiscalyear=parameter_dict['fiscal_year'], 
                                                       target_move=parameter_dict['target_move'], 
                                                       unreconcile=False, 
                                                       historic_strict=False, 
                                                       special_period=False, 
                                                       context=context)
        
        #account_dict is a dictionary where key is account_id and it has all move_lines for each account.
        return account_dict
    
    #4. Build data for report
    def get_data(self, cr, uid, data,context):

        distribution_obj = self.pool.get('account.cash.flow.distribution')
        cash_flow_amounts = {} # contains amounts for each cash_flow_types
        cash_flow_types = {}   # Groups by type    
        total_by_type = {}     # Return total amount by type
        
        #===========================================================
        
        #Get move_lines
        account_dict = self.get_move_lines(cr, uid, data, context)
        
        #Find if lines have a distribution_line
        for account, move_lines in account_dict.iteritems():
            for line in move_lines:
                amount_debit = 0
                amount_credit = 0.0
                
                #Get debit and credit from original line. 
                if line.debit > 0:
                    amount_debit = line.debit
                elif line.credit > 0:
                    amount_credit = line.credit
                    
                #Search all distribution_lines that are asociated to line
                lines_distribution = distribution_obj.search(cr, uid, [('account_move_line_id', '=', line.id)])
                lines_distribution_list = distribution_obj.browse(cr, uid, lines_distribution)
                
                #Only if accounts have cash_flow_type
                for line_distribution in lines_distribution_list:
                    if line_distribution.target_account_move_line.account_id.cash_flow_type:
                        cash_flow_type = line_distribution.target_account_move_line.account_id.cash_flow_type
#                        ====================================================================
#                        Create a dictionary, where key is cash_flow_type id. Create a list, with type, amount and name of
#                        cash_flow. Then, iterate this dictionary and group for type and print in report.
#                        List order = [type, debit, credit, amount, name]
#                        ====================================================================
                        if cash_flow_type:
                            if cash_flow_type.id not in cash_flow_amounts.keys():
                                target_amount = line_distribution.target_account_move_line.debit + line_distribution.target_account_move_line.credit
                                list = [cash_flow_type.type, amount_debit, amount_credit, target_amount, cash_flow_type.name]
                                cash_flow_amounts[cash_flow_type.id] = list                            
                            else:
                                temp_list = cash_flow_amounts[cash_flow_type.id]
                                #======= Update amounts                                
                                target_new_amount = line_distribution.target_account_move_line.debit + line_distribution.target_account_move_line.credit
                                temp_list[1] += amount_debit
                                temp_list[2] += amount_credit
                                temp_list[3] += target_new_amount
                                cash_flow_amounts[cash_flow_type.id] = temp_list
                                
        #========================================================================
        
        #Group in types (operational, investment, financing). Create list of each type (with id)
        #This connect dictionary with amounts (cash_flow_amounts) and dictionary with types.
        #example = {'operational': 1, 3, 4} -> cash_flow_id
        for type_id, items in cash_flow_amounts.iteritems():
            type_name = items[0]
            if type_name not in cash_flow_types.keys():
                cash_flow_types[type_name] = [type_id] #position 2 is id of cash_flow_type. Create a list with id of cash_flow_type.
            
            else:
                list = cash_flow_types[type_name] 
                list.append(type_id) #Add new id
                cash_flow_types[type_name] = list
                list = []
        
        
        #========================================================================
        amount = 0.0
        #Group totals by type, return a dictionary with totals.
        #Iterate in each id and sum, in cash_flow_amounts
        for type, list_ids in cash_flow_types.iteritems():
            for item in list_ids:
                if item in cash_flow_amounts.keys():
                    list_values = cash_flow_amounts[item] #extract info from cash_flow_amounts
                    amount += list_values[3] #amount for type.
            
            #for example
            #total_by_type['operational'] = ₡40 000
            total_by_type[type] = amount
       
        #=========================================================================
       
        #====RETURN THREE DICTIONARIES
        # 1. CASH_FLOW_AMOUNTS = Contains total amount, debit and credit for each cash_flow type
        # 2. CASH_FLOW_TYPES =  Return type_cash_flow as key (operational, investment and financing) and a list of ids of cash_flow_types that 
        # are associated of one of those types.
        # 3. TOTAL_BY_TYPE = Return a dictionary, where key is one type and it has total amount for each type.
        
        
        #If there not exist data, return empty dictionaries
        if not cash_flow_amounts:
            cash_flow_types = {
                               'operation': [],
                               'investment': [],
                               'financing': [],
                               }
            total_by_type = {
                               'operation':0.0,
                               'investment': 0.0,
                               'financing':0.0,
                               }

        return cash_flow_amounts, cash_flow_types, total_by_type
    