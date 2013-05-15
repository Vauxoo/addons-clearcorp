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

from openerp.addons.account_financial_report_webkit.report.common_reports import CommonReportHeaderWebkit
import pooler
from report import report_sxw

class GeneralLedgerReportWebkit(report_sxw.rml_parse, CommonReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(GeneralLedgerReportWebkit, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'get_data':self.get_data,  
            'get_chart_account_id':self._get_chart_account_id_br,
            'get_fiscalyear':self.get_fiscalyear_br,      
            'get_filter': self._get_filter,   
            'get_start_period':self.get_start_period_br,
            'get_end_period':self.get_end_period_br,
            'get_start_date':self._get_date_from,
            'get_stop_date':self._get_date_to,
            'accounts': self._get_accounts_br,
            'display_target_move': self._get_display_target_move,
            'extract_name_move': self.extract_name_move,
        })

    def get_data(self, cr, uid, data):
        filter_data = []
        account_list = []
        account_selected = []
        conciliation_lines = [] 
        
        account_lines = {}
        account_balance = {}
        account_conciliation = {}
        account_move_line_con = {}
                
        library_obj = self.pool.get('account.webkit.report.library')
        
        filter_type = self._get_form_param('filter', data, default='filter_no')
        chart_account = self._get_chart_account_id_br(data)
        
        if filter_type == 'filter_date':
            start_date = self._get_form_param('date_from', data)
            stop_date = self._get_form_param('date_to', data)
            
            filter_data.append(start_date)
            filter_data.append(stop_date)
            
        elif filter_type == 'filter_period':
            
            start_period = self.get_start_period_br(data) #return the period object
            stop_period = self.get_end_period_br(data)
            
            filter_data.append(start_period)
            filter_data.append(stop_period)
            
        else:
            filter_type = ''
        
        fiscalyear = self.get_fiscalyear_br(data)
        target_move = self._get_form_param('target_move', data, default='all')
        
        #From the wizard can select specific account, extract this accounts
        account_selected = data['form']['account_ids']

        #Prepare the account_id list. 
        if account_selected == []:
            account_list_ids = library_obj.get_account_child_ids(cr, uid, chart_account.id) #get all the accounts in the chart_account_id
            account_list_obj = self.pool.get('account.account').browse(cr, uid, account_list_ids)
            for account in account_list_obj:
                conciliation_lines = []
                if  account.type != 'view':
                    #Get the move_lines for each account.
                    move_lines = library_obj.get_move_lines(cr, uid,
                                                            [account.id], 
                                                            filter_type=filter_type, 
                                                            filter_data=filter_data, 
                                                            fiscalyear=fiscalyear, 
                                                            target_move=target_move,
                                                            order_by='asc')
                    if account.id not in account_lines.keys():
                       account_lines[account] = move_lines
                    
                    #Reconcile -> show reconcile in the mako.
                    '''
                    First, if the account permit reconcile (reconcile == True), add to the dictionary.
                    If the account don't allow the reconcile, search if the lines have reconcile_id or partial_reconcile_id
                    If the account allow the reconcile or the lines have reconcile_id or partial_reconcile_id, add in the dictionary
                    and show in the mako the column "Reconcile"
                    
                    the final result is:
                       {account_id: {line.id: [conciliation_name]}}
                    '''
                    #1. If the account have reconcile, add to the dictionary
                    if account.reconcile and account.id not in account_conciliation:
                        account_conciliation[account.id] = []
                    
                    #Search if the move_lines have partial or reconcile id
                    for line in move_lines:
                        if line.reconcile_id and line.reconcile_id.name != '':
                            conciliation_lines.append(line.reconcile_id.name)
                         
                        elif line.reconcile_partial_id and line.reconcile_partial_id.name != '':
                            str_name = 'P' + line.reconcile_id.name
                            conciliation_lines.append(str_name)
                        
                        #Add the line.id and the name of the conciliation.
                        if len(conciliation_lines) > 0: 
                             account_move_line_con[line.id] = conciliation_lines
                        
                        #Clean the name of the conciliation
                        conciliation_lines = []
                    
                    #After the search in each lines, add the dictionary (key: line.id, value: conciliation_name)
                    #with account.id (key of the principal dictionary) and match the account_id with the conciliation name.                    
                    if account.id in account_conciliation.keys():
                        account_conciliation[account.id] = account_move_line_con
                    
                    elif account.id not in account_conciliation.keys() and len(account_move_line_con) > 0: 
                        account_conciliation[account.id] = account_move_line_con
                        
            #Get the initial_balance for the account
            for account in account_list_obj:
                if  account.type != 'view':
                    account_list.append(account.id)

            if filter_type == 'filter_date':
                account_balance = library_obj.get_account_balance(cr, uid, 
                                                                  account_list,
                                                                  ['balance'],
                                                                  initial_balance=True,
                                                                  company_id=chart_account.company_id.id,
                                                                  fiscal_year_id = fiscalyear.id,
                                                                  state = target_move,
                                                                  start_date = start_date,
                                                                  stop_date = stop_date,
                                                                  chart_account_id = chart_account.id,
                                                                  filter_type=filter_type)
            elif filter_type == 'filter_period':
                account_balance = library_obj.get_account_balance(cr, uid, 
                                                                  account_list,
                                                                  ['balance'],
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
                                                                  account_list,
                                                                  ['balance'],
                                                                  initial_balance=True,
                                                                  company_id=chart_account.company_id.id,
                                                                  fiscal_year_id = fiscalyear.id,
                                                                  state = target_move,
                                                                  chart_account_id = chart_account.id,
                                                                  filter_type=filter_type)
        else:
            account_list_ids = library_obj.get_account_child_ids(cr, uid, account_selected) #get all the accounts in the chart_account_id
            account_list_obj = self.pool.get('account.account').browse(cr, uid, account_list_ids)
            for account in account_list_obj:
                if  account.type != 'view':
                     move_lines = library_obj.get_move_lines(cr, uid,
                                                             [account.id], 
                                                            filter_type=filter_type, 
                                                            filter_data=filter_data, 
                                                            fiscalyear=fiscalyear, 
                                                            target_move=target_move,
                                                            order_by='asc')
                
                     if account.id not in account_lines.keys():
                         account_lines[account] = move_lines
                    
                     #Reconcile -> show reconcile in the mako.
                     '''
                     First, if the account permit reconcile (reconcile == True), add to the dictionary.
                     If the account don't allow the reconcile, search if the lines have reconcile_id or partial_reconcile_id
                     If the account allow the reconcile or the lines have reconcile_id or partial_reconcile_id, add in the dictionary
                     and show in the mako the column "Reconcile"
                    
                     the final result is:
                        {account_id: {line.id: [conciliation_name]}}
                     '''
                     #1. If the account have reconcile, add to the dictionary
                     if account.reconcile and account.id not in account_conciliation:
                         account_conciliation[account.id] = []
                    
                     #Search if the move_lines have partial or reconcile id
                     for line in move_lines:
                         if line.reconcile_id and line.reconcile_id.name != '':
                             conciliation_lines.append(line.reconcile_id.name)
                         
                         elif line.reconcile_partial_id and line.reconcile_partial_id.name != '':
                             str_name = 'P' + line.reconcile_id.name
                             conciliation_lines.append(str_name)
                        
                         #Add the line.id and the name of the conciliation.
                         if len(conciliation_lines) > 0: 
                             account_move_line_con[line.id] = conciliation_lines
                        
                         #Clean the name of the conciliation
                         conciliation_lines = []
                    
                     #After the search in each lines, add the dictionary (key: line.id, value: conciliation_name)
                     #with account.id (key of the principal dictionary) and match the account_id with the conciliation name.                    
                     if account.id in account_conciliation.keys():
                         account_conciliation[account.id] = account_move_line_con
                    
                     elif account.id not in account_conciliation.keys() and len(account_move_line_con) > 0: 
                         account_conciliation[account.id] = account_move_line_con
            
            #Get the initial_balance for the account
            for account in account_list_obj:
                if  account.type != 'view':
                    account_list.append(account.id)

            if filter_type == 'filter_date':
                account_balance = library_obj.get_account_balance(cr, uid, 
                                                                  account_list,
                                                                  ['balance'],
                                                                  initial_balance=True,
                                                                  company_id=chart_account.company_id.id,
                                                                  fiscal_year_id = fiscalyear.id,
                                                                  state = target_move,
                                                                  start_date = start_date,
                                                                  stop_date = stop_date,
                                                                  chart_account_id = chart_account.id,
                                                                  filter_type=filter_type)
            elif filter_type == 'filter_period':
                account_balance = library_obj.get_account_balance(cr, uid, 
                                                                  account_list,
                                                                  ['balance'],
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
                                                                  account_list,
                                                                  ['balance'],
                                                                  initial_balance=True,
                                                                  company_id=chart_account.company_id.id,
                                                                  fiscal_year_id = fiscalyear.id,
                                                                  state = target_move,
                                                                  chart_account_id = chart_account.id,
                                                                  filter_type=filter_type)
        
        return account_lines, account_balance, account_conciliation
    
    ''''
    This method is created to solve the error when extracting the name move_id (line.move_id.name) fails because of read permissions
    parameter move_lines are the move_lines that match with the journal and period. Pass from mako. 
    ''' 
    def extract_name_move(self, cr, uid, move_lines):
        move_temp = self.pool.get('account.move')
        dict_name = {} #dict_name keys is the line id. 
        
        for line in move_lines:
            move_id = move_temp.search(cr, uid, [('id', '=', line.move_id.id)])
            move_obj = move_temp.browse(cr, uid, move_id)
            if move_obj[0].name:
                dict_name[line.id] = move_obj[0].name
            else:
                 dict_name[line.id] = move_obj[0].id
        
        return dict_name
    
report_sxw.report_sxw('report.account_general_ledger_webkit',
                             'account.account',
                             'addons/account_general_ledger_report/report/account_general_ledger_report.mako',
                             parser=GeneralLedgerReportWebkit)