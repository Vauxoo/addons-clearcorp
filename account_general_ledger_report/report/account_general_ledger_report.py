#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.addons.account_report_lib.account_report_base import accountReportbase
from report import report_sxw

class Parser(accountReportbase):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'get_data':self.get_data,            
               
            #====================SET AND GET METHODS ===========================
            'storage':{},
            'cumul_balance': None,
            'cumul_balance_curr': None,
            'get_conciliation_name':self.get_conciliation_name,
            'set_data_template': self.set_data_template,
            'get_data_template': self.get_data_template,
            'get_cumul_balance': self.get_cumul_balance,
            'get_cumul_balance_foreing_curr': self.get_cumul_balance_foreing_curr,
            'get_total_cumul_balance':self.get_total_cumul_balance,
            'get_total_cumul_balance_curr':self.get_total_cumul_balance_curr,
            'compute_cumul_balance': self.compute_cumul_balance,
            'compute_cumul_balance_foreign': self.compute_cumul_balance_foreign,
            'compute_debit':self.compute_debit,
            'compute_credit':self.compute_credit,
            'compute_amount_total_curr':self.compute_amount_total_curr,
            #===================================================================
            
            #=====================DISPLAY DATA==================================
            'account_has_reconcile_column': self.account_has_reconcile_column,
            'account_has_currrency_id': self.account_has_currrency_id, 
            
            #====================RESET VALUES ==========================#
            'reset_balances': self.reset_balances, 
        })
    
    #set data to use in odt template. 
    def set_data_template(self, cr, uid, data):        
        
        account_list_obj, account_lines, account_conciliation, account_balance = self.get_data(cr, uid, data)
        
        dict_update = {
                       'account_list_obj': account_list_obj,
                       'account_lines': account_lines,
                       'account_conciliation': account_conciliation, 
                       'account_balance': account_balance,
                      }
        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #Return the cumul_balance for a specific account. Return cumul_balance
    #variable from localcontext
    def get_total_cumul_balance(self):
        return self.localcontext['cumul_balance']
    
    #Return the cumul_balance_curr for a specific account. Return cumul_balance_curr
    #variable from localcontext
    def get_total_cumul_balance_curr(self):
        return self.localcontext['cumul_balance_curr']
    
    #Return the acumulated balance for a specific account.
    """@param account: account is a browse record. It's comming for the odt template """
    def get_cumul_balance(self, account):
       account_balance = self.localcontext['storage']['account_balance']
       return account_balance[account.id]['balance'] or 0.0
   
    #Return the acumulated balance for a foreign account.   
    """@param account: account is a browse record. It's comming for the odt template """
    def get_cumul_balance_foreing_curr(self, account):
        account_balance = self.localcontext['storage']['account_balance']
        if 'foreign_balance' in account_balance[account.id].keys():
            return account_balance[account.id]['foreign_balance']   
        else:
            return 0.0
    
    #Create a string with name of conciliation. Add a 'P' for partial
    def get_conciliation_name(self, line):
        if line.reconcile_id and line.reconcile_id.name != '':
            return line.reconcile_id.name
        
        elif line.reconcile_partial_id and line.reconcile_partial_id.name != '':
            str_name = 'P: ' + line.reconcile_partial_id.name
            return str_name
        else:
            return ''
        
    #===THIS METHODS ARE FOR DISPLAY DIFFERENTS HEADERS DEPENDS OF VALUES IN ACCOUNT    
    #Has_reconcile
    def account_has_reconcile_column(self, account):
        if account.reconcile or (account.id in self.localcontext['storage']['account_conciliation'].keys() and self.localcontext['storage']['account_conciliation'][account.id]):
            return True
        return False
    
    #Has_foreing_currency
    def account_has_currrency_id (self, account):
        if account.report_currency_id:
            return True
        return False
    
    #==== THIS METHODS ARE TO COMPUTE TEMPORALLY VARIABLES IN ODT TEMPLATE=====
    def compute_cumul_balance(self, account, line):   
        # The first time, cumul_balance takes balance for account, 
        # then, get this value and compute with debit and credit values from line.
        cumul_balance = self.localcontext['cumul_balance']
        
        if cumul_balance:
            cumul_balance = cumul_balance + line.debit - line.credit
            self.localcontext['cumul_balance'] = cumul_balance
        
        else:
            cumul_balance = self.get_cumul_balance(account)
            cumul_balance = cumul_balance + line.debit - line.credit
            self.localcontext['cumul_balance'] = cumul_balance
        
        return cumul_balance
    
    def compute_cumul_balance_foreign(self, account, line):
        # The first time, cumul_balance takes balance for account, 
        # then, get this value and compute with debit and credit values from line.
        cumul_balance_curr = self.localcontext['cumul_balance_curr']
        
        if cumul_balance_curr:
            cumul_balance_curr = cumul_balance_curr + line.debit - line.credit
            self.localcontext['cumul_balance_curr'] = cumul_balance_curr
        
        else:
            cumul_balance_curr = self.get_cumul_balance_foreing_curr(account)
            cumul_balance_curr = cumul_balance_curr + line.debit - line.credit
            self.localcontext['cumul_balance_curr'] = cumul_balance_curr
        
        return cumul_balance_curr
    
    #====== COMPUTE EACH TOTAL FOR EACH COLUMN ======#
    def compute_amount_total_curr(self, move_lines):
        total = 0.0        
        for line in move_lines:
            total += line.amount_currency        
        return total
    
    def compute_debit (self, move_lines):
        total = 0.0        
        for line in move_lines:
            total += line.debit
        return total
    
    def compute_credit (self, move_lines):
        total = 0.0        
        for line in move_lines:
            total += line.credit
        return total
    
    #======METHODS TO RESET VALUES ====#
    def reset_balances(self):
        self.localcontext['cumul_balance'] = None
        self.localcontext['cumul_balance_curr'] = None
        
        return True
               
   #==========================================================================

    def get_data(self, cr, uid, data):
        filter_data = []
        account_list = []        
        account_selected = []
        
        account_lines = {}
        account_balance = {}
        account_conciliation = {}
                
        library_obj = self.pool.get('account.webkit.report.library')
        
        filter_type = self.get_filter(data)
        chart_account = self.get_chart_account_id(data)
        
        if filter_type == 'filter_date':
            start_date = self.get_date_from(data)
            stop_date = self.get_date_to(data)
            
            filter_data.append(start_date)
            filter_data.append(stop_date)
            
        elif filter_type == 'filter_period':
            
            start_period = self.get_start_period(data) #return the period object
            stop_period = self.get_end_period(data)
            
            filter_data.append(start_period)
            filter_data.append(stop_period)
            
        else:
            filter_type = ''
        
        fiscalyear = self.get_fiscalyear(data)
        target_move = self.get_target_move(data)
        
        #From the wizard can select specific account, extract this accounts
        account_selected = self.get_accounts_ids(cr, uid, data)
        
        if not account_selected:
            account_selected = [chart_account.id]
            account_list_ids = library_obj.get_account_child_ids(cr, uid, account_selected) #get all the accounts in the chart_account_id
        
        #Extract the id for the browse record
        else:
            account_ids = []
            for account in account_selected:
                account_ids.append(account.id)
                account_list_ids = library_obj.get_account_child_ids(cr, uid, account_ids) #get all the accounts in the chart_account_id
        
        account_list_obj = self.pool.get('account.account').browse(cr, uid, account_list_ids)
          
        #Get the move_lines for each account.
        move_lines = library_obj.get_move_lines(cr, 1,
                                                account_list_ids, 
                                                filter_type=filter_type, 
                                                filter_data=filter_data, 
                                                fiscalyear=fiscalyear, 
                                                target_move=target_move,
                                                order_by='account_id asc, date asc, ref asc')
        
       
        #Reconcile -> show reconcile in the mako.
        '''
        First, if the account permit reconcile (reconcile == True), add to the dictionary.
        If the account don't allow the reconcile, search if the lines have reconcile_id or partial_reconcile_id
        If the account allow the reconcile or the lines have reconcile_id or partial_reconcile_id, add in the dictionary
        and show in the mako the column "Reconcile"
        
        the final result is:
           {account_id: {line.id: [conciliation_name]}}
        '''        
        #Search if the move_lines have partial or reconcile id
        for line in move_lines:           
            #If the account have reconcile, add to the dictionary              
            if line.account_id.id not in account_conciliation:
                account_conciliation[line.account_id.id] = {}
            
            if line.reconcile_id and line.reconcile_id.name != '':
                 account_conciliation[line.account_id.id][line.id] = line.reconcile_id.name
             
            elif line.reconcile_partial_id and line.reconcile_partial_id.name != '':
                str_name = 'P: ' + line.reconcile_partial_id.name
                #conciliation_lines.append(str_name)
                account_conciliation[line.account_id.id][line.id] = str_name             
            
            if line.account_id.id not in account_lines:
                account_lines[line.account_id.id] = []
            
            account_lines[line.account_id.id].append(line)
        
        fields = ['balance']            
        if self.get_amount_currency(data):
            fields.append('foreign_balance')
        
        if filter_type == 'filter_date':
            account_balance = library_obj.get_account_balance(cr, uid, 
                                                              account_list_ids,
                                                              fields,
                                                              initial_balance=True,
                                                              company_id=chart_account.company_id.id,
                                                              fiscal_year_id = fiscalyear.id,
                                                              state = target_move,
                                                              start_date = start_date,
                                                              end_date = stop_date,
                                                              chart_account_id = chart_account.id,
                                                              filter_type=filter_type)
        elif filter_type == 'filter_period':
            account_balance = library_obj.get_account_balance(cr, uid, 
                                                              account_list_ids,
                                                              fields,
                                                              initial_balance=True,
                                                              company_id=chart_account.company_id.id,
                                                              fiscal_year_id = fiscalyear.id,
                                                              state = target_move,
                                                              start_period_id = start_period.id,
                                                              end_period_id = stop_period.id,
                                                              chart_account_id = chart_account.id,
                                                              filter_type=filter_type)
        else:
            account_balance = library_obj.get_account_balance(cr, uid, 
                                                              account_list_ids,
                                                              fields,
                                                              initial_balance=True,
                                                              company_id=chart_account.company_id.id,
                                                              fiscal_year_id = fiscalyear.id,
                                                              state = target_move,
                                                              chart_account_id = chart_account.id,
                                                              filter_type=filter_type)
        
        
        return account_list_obj, account_lines, account_conciliation, account_balance
