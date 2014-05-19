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

import copy
import netsvc
from osv import fields, orm
import tools

class AccountWebkitReportLibrary(orm.Model):
    
    _name =  "account.webkit.report.library"
    _description = "Account Webkit Reporting Library"
    
    def get_move_lines(self, cr, uid, account_ids, filter_type='', filter_data=None, fiscalyear=None, target_move='all', unreconcile = False, historic_strict=False, special_period =False, order_by=None, context=None):
        ''' Get the move lines of the accounts provided and filtered.
        Arguments:
        'account_ids': List of accounts ids.
        'filter_type': Filter used, possibles values: 'filter_date', 'filter_period' or ''.
        'filter_data': If filter is by date then filter_data is a list of strings with the initial date and the ending date, if filter is by period then
                       filter_data is a list of browse record with the initial period and the ending period.
        'fiscalyear':  Browse record of the fiscal year selected.
        'target_move': Target moves of the report, possibles values: 'all' or 'posted'.
        'unreconcile': If True then get the move lines unreconciled.
        'historic_strict': Used when unreconcile = True, forces to include move lines that where not reconciled at the end date of the filter but are now.
        'order_by': Used to the lines return order by specific order. asc or desc are the accepted words.
         
        '''
        """
            Previously, method get_move_lines only was used in Conciliation Bank Report. This report doesn't used start period as a parameter, so method
            didn't include start_period in method get_move_lines. start_period parameter is necessary for many reports, for example in Bank Account Balance Report.
            For that reason, it was necessary make a change in Conciliation Bank Report, that change was initialize start_period in None and changes Conciliation
            Bank report doesn't consider start_period as parameter.
            
            In standard library it's necessary, also, specified if start_period is None, doesn't consider as parameter or if it has information, take as 
            start_period parameter and put with other filters in method. start_period is used to build periods range and pass it to method.
            
            It modifies Conciliation Bank Report and standard library for both work only with final period or with a range of periods (as Bank Account Balance Report).
            In the case of dates, it works at the same way (The balances of Bank Account Balance Report takes start_date as parameter)
            
            If's sequences were eliminated and they were replaced for a unique domain. This action increase method's preformance   
        """
           
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = []
        list_tuples = []
       
#        search domains are constructed in a list of tuples. It makes a search domaind depend of parameters
#        search domain is builted for get account.move.lines that match with final search domain.
        
        #*******************************BUILD SEARCH DOMAINS***************************#
#       if filter_data and filter_type are None (they don't have data) and fiscal_year doesn't exist
#       the method takes accounts that match with target_move parameter.
 
        #********account_ids ******#
        domain = ('account_id', 'in', account_ids)
        list_tuples.append(domain)        
        
        #********target_mvove ******#
        if not target_move == 'all':
            domain = ('move_id.state', '=', target_move)
            list_tuples.append(domain)        
        
        #********Filter by date, period or filter_type = '' *********#
        if filter_type == 'filter_date':
            if filter_data[0] is None: #it takes only final_date.
                date_stop = filter_data[1]
                domain = ('date', '<=', date_stop)
                list_tuples.append(domain)
            else:
                domain_start_date = ('date', '>=', filter_data[0])
                domain_stop_date = ('date', '<=', filter_data[1])
                list_tuples.append(domain_start_date)
                list_tuples.append(domain_stop_date)                

        elif filter_type == 'filter_period':
            period_domain_list = []
            date_stop = ('date_stop', '<=', filter_data[1].date_stop)
            period_domain_list.append(date_stop)
            #It is considered fiscal_year and special_period.
            if fiscalyear:
                fiscal_year = ('fiscalyear_id', '=', fiscalyear.id)
                period_domain_list.append(fiscal_year)
            if special_period == False:
                special = ('special', '=', False)
            else:
                special = ('special', '=', True)
            period_domain_list.append(special)
            
            if filter_data[0]: 
                #This case is for reports that take initial_period or initial_date as parameter
                date_start = ('date_start', '>=', filter_data[0].date_start)
                period_domain_list.append(date_start)
            
            #In final search domain, it takes fiscal_year, special periods, and start/end period
            periods_ids = self.pool.get('account.period').search(cr, uid,period_domain_list, context=context)
                
            #Get periods with previous ids.
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
        
        #If filter doesn't exist, but fiscal_year exist, get periods that match with fiscal_year
        #special_period parameter indicates that special periods are considered.
        elif filter_type == '' and fiscalyear:
            if special_period is True:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', True),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            else:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', False),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
                    
        #**********************************************************************************************#
        
        if unreconcile == False:
            move_line_ids = move_line_obj.search(cr, uid, list_tuples,order = order_by,context=context)
                
        else:
            #list_tuples + [domain_unreconciled] -> With this syntax doesn't change the variable
            #list_tuples, the + makes a complete list with domain_unreconciled. Add [] for make as a format list.
            
            #First, move line ids without reconcile_id (without conciliation)
            domain_unreconciled = ('reconcile_id', '=', None)      
            unreconciled_move_line_ids = move_line_obj.search(cr, uid, list_tuples + [domain_unreconciled], context=context)
            
            #historict_strict = If user needs a historic strict (this option obtains all move lines
            #without conciliation to the date requested in report.)  
            if historic_strict == False:
                move_line_ids = unreconciled_move_line_ids
                
            #Mark historic_strict as True
            else: 
                #Get maximal conciliation date to get move lines.
                if filter_type == 'filter_date':
                    #maximal conciliation date is date selected
                    max_reconciled_date = filter_data[1]    
                elif filter_type == 'filter_period':
                    #maximal conciliation date is final date of selected period
                    max_reconciled_date = filter_data[1].date_stop
                elif fiscalyear:
                    #If only fiscalyear exists, it takes end_date as maximal conciliation date
                    max_reconciled_date = fiscalyear.date_end
                else:
                    max_reconciled_date = False
                
                #If maximal date exists, get move lines without conciliation
                #It is to compare unreconciled lines vrs reconciled lines.
                #If any date_crete in unreconciled lines is more than maximal date of conciliation,
                # add in list of unreconciled lines.
                if max_reconciled_date:
                    domain_reconciled = ('reconcile_id', '<>', None)  
                    reconciled_move_line_ids = move_line_obj.search(cr, uid, list_tuples + [domain_reconciled], context=context)
                    reconciled_move_lines = move_line_obj.browse(cr, uid, reconciled_move_line_ids, context=context)
                    for line in reconciled_move_lines:
                        if line.reconcile_id:
                            if line.reconcile_id.create_date > max_reconciled_date:
                                unreconciled_move_line_ids.append(line.id)
                    
                move_line_ids = unreconciled_move_line_ids
              
        move_lines = move_line_ids and move_line_obj.browse(cr, uid, move_line_ids, context=context) or []
        
        return move_lines
    
    def get_account_balance(self, cr, uid,
                            account_ids,
                            field_names,
                            initial_balance=False,
                            company_id=False,
                            fiscal_year_id=False,
                            all_fiscal_years=False,
                            state='all',
                            start_date=False,
                            end_date=False,
                            start_period_id=False,
                            end_period_id=False,
                            period_ids=False,
                            journal_ids=False,
                            chart_account_id=False,
                            filter_type = '',
                            context={}):
        ''' Get the balance for the provided account ids with the provided filters
        Arguments:
        account_ids:        [int], required, account ids
        field_names:        ['balance', 'debit', 'credit', 'foreign_balance'], the fields to compute
        initial_balance:    bool, True if the return must be the initial balance for the period of time specified, not the ending balance.
        company_id:         int, id for the company
        fiscal_year_id:     int, id for the fiscal year
        all_fiscal_years:   bool, True if all fiscal years must be used, including the closed ones. (usefull for receivable for ex.)
        state:              selection of: draft, posted, all; the state of the move lines used in the calculation
        start_date:         date string, start date
        end_date:           date string, end date
        start_period_id:    int, start period id
        end_period_id:      int, end period id
        period_ids:         list of int, list of periods ids used
        journal_ids:        list of int, list of journal ids used
        chart_account_id:   int, chart of account used
        filter_type:        string, tipo de filtro seleccionado.
        
        If there is an end_period without a start_period, all precedent moves for the end period will be used.
        If there isn't a fiscal year, all open fiscal years will be used. To include all closed fiscal years, the all_fiscal_years must be True.
        '''
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        context_copy = copy.copy(context)
        context = {}
        
        if company_id:
            context.update({'company_id':company_id})
        if fiscal_year_id:
            context.update({'fiscalyear':fiscal_year_id})
        if all_fiscal_years:
            context.update({'all_fiscalyear':all_fiscal_years})
        if state:
            context.update({'state':state})
        if start_date:
            context.update({'date_from':start_date})
        if end_date:
            context.update({'date_to':end_date})
        if journal_ids:
            context.update({'journal_ids':journal_ids})
        if chart_account_id:
            context.update({'chart_account_id':chart_account_id})
                
        """
            Variable initial_balance = True, if it is necessary get initial balance. If initial_balance is false is an "ordinary" balance.
            If user needs initial balance, there are two options:
                1. Get initial balance with a range of periods: Gets previous period to period selected and previous period needs match with fiscal year (end_period_id variable).
                2. Get initial balance with only end period: Gets a period list until final period, those ids are period_ids variable. end_period_id is open period. 
            
            If user needs ordinary balance, there are two options:
                1. If start period and end period exist, get periods list between them and fiscal_year
                2. If only exist end_period: Get fiscal_year and end_period_id is period selected.
        """
        
        #fiscal_year        
        fiscal_year = self.pool.get('account.fiscalyear').browse(cr,uid,fiscal_year_id)
        
        if start_period_id:
            start_period = self.pool.get('account.period').browse(cr,uid,start_period_id)
        if end_period_id:
            end_period = self.pool.get('account.period').browse(cr,uid,end_period_id)
                    
        if filter_type == 'filter_period':
            #Get initial_balance
            if initial_balance == True:
                # If start period and end period exist -> Calculate the list of periods until the initial period selected. The start_period_id 
                # is period before period selected.
                if start_period_id and end_period_id:
                    start_period_id = self.pool.get('account.period').get_start_previous_period(cr, uid, start_period=start_period, fiscal_year=fiscal_year)
                    start_period = self.pool.get('account.period').browse(cr, uid, start_period_id)
                    period_ids = self.pool.get('account.period').get_interval_period(cr, uid, start_period=start_period, end_period = end_period, fiscal_year=fiscal_year_id, initial_balance=True)
                                       
                # If only final period is selected -> Get range of periods until the period end.
                # end_period_id = The "oldest" opening period in fiscal_year
                if (not start_period_id and end_period_id):
                    period_ids = self.get_interval_period(cr, uid, end_period=end_period, fiscal_year=fiscal_year_id,initial_balance=True)
                    
            #Ordinary balance
            else:
                #only select a period: End period
                if not period_ids and fiscal_year_id and not start_period_id and end_period_id:
                    end_period = period_obj.browse(cr, uid, end_period_id)
                    period_ids = period_obj.search(cr, uid, ['&',('fiscalyear_id','=',fiscal_year_id),('date_stop', '<=', end_period.date_stop)], context=context)
                
                #Selected both periods
                if not period_ids and fiscal_year_id and start_period_id and end_period_id:
                    start_period = period_obj.browse(cr, uid, start_period_id)
                    end_period = period_obj.browse(cr, uid, end_period_id)
                    period_ids = period_obj.get_interval_period(cr, uid, start_period=start_period, end_period=end_period, fiscal_year=fiscal_year_id)
                
                #Only ordinary period needs start_period.
                if start_period_id:
                    context.update({'period_from':start_period_id})
        
        # If there are no filters, find the first special period of fiscal       
        if filter_type == '':       
            if initial_balance:
                period_ids = [self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',fiscal_year_id),('special','=',True)],order='date_start asc')[0]]
            else:
                period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=', fiscal_year_id)] )        
        
        #####################################################################
        
        if end_period_id:
            context.update({'period_to':end_period_id})
        
        if period_ids:
            context.update({'periods':period_ids})
        
        '''
        Description for the __compute method:
        Get the balance for the provided account ids with the provided filters
        Arguments:
        `account_ids`: list, account ids
        `field_names`: list, the fields to compute (valid values:
                       'balance', 'debit', 'credit', foreign_balance)
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        'context': The context have the filters for the move lines, to see the proper keys and values that should be used check
                   the method _query_get of account_move_line
                   initial_bal:         bool, True if the return must be the initial balance for the period of time specified, not the ending balance.
                   company_id:          int, id for the company, if provided only moves for that company will be used
                   fiscalyear:          int, id for the fiscal year, if provided only moves for that fiscal year will be used
                   all_fiscalyear:      bool, True if all fiscal years must be used, including the closed ones. (usefull for receivable for ex.)
                   state:               selection of: draft, posted, all; the state of the move lines used in the calculation
                   date_from:           date string, start date
                   date_to:             date string, end date
                   period_from:         int, start period id
                   period_to:           int, end period id
                   periods:             list of int, list of periods ids used
                   journal_ids:         list of int, list of journal ids used
                   chart_account_id:    int, chart of account used
        '''
        res = account_obj._account_account__compute(cr, uid, account_ids, field_names, context=context)
        context = context_copy
        
        return res
        
    def get_balance_tmp(self, cr, uid, account_ids, field_names, arg=None, context=None,
                    query='', query_params=()):
        ''' Get the balance for the provided account ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        'context': The context have the filters for the move lines, to see the proper keys and values that should be used check
                   the method _query_get of account_move_line
        '''
        account_obj = self.pool.get('account.account')
        
        res = account_obj._account_account__compute(cr, uid, account_ids, field_names, arg=arg, context=context,
                    query=query, query_params=query_params)
        
        return res
    
    #Return child of a specific list of ids (account_ids)
    def get_account_child_ids(self, cr, uid, account_ids, context={}):
        if isinstance(account_ids, orm.browse_record):
            account_ids = [account_ids.id]
        elif isinstance(account_ids, int):
            account_ids = [account_ids]
        return self.pool.get('account.account')._get_children_and_consol(cr, uid, account_ids, context=context)
    
    #returns amount of the currency symbol + position    
    def format_lang_currency (self, cr, uid, amount_currency, currency):
        format_currency = ''
        
        if currency:
           if currency.symbol_prefix:
                format_currency =  currency.symbol_prefix + ' ' + amount_currency
           else:
                format_currency = amount_currency+ ' ' +  currency.symbol_sufix
        else:
            format_currency = amount_currency
            
        return format_currency
    
    #move lines from a specific journal
    def get_move_lines_journal(self, cr, uid, journal_ids, filter_type='', filter_data=None, fiscalyear=None, target_move='all', unreconcile = False, historic_strict=False, special_period =False, order_by=None, context=None):
        
        ''' 
        Get the move lines of the journal provided and filtered.
        
        Arguments:
        'journal_ids': List of journal ids.
        'filter_type': Filter used, possibles values: 'filter_date', 'filter_period' or ''.
        'filter_data': If filter is by date then filter_data is a list of strings with the initial date and the ending date, if filter is by period then
                       filter_data is a list of browse record with the initial period and the ending period.
        'fiscalyear':  Browse record of the fiscal year selected.
        'target_move': Target moves of the report, possibles values: 'all' or 'posted'.
        'order_by': Used to the lines return order by specific order. asc or desc are the accepted words. Also, we can specified which field is going to be used
         
        '''
        
        journal_obj = self.pool.get('account.journal')
        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = []
        list_tuples = []
       
        #===============================================================================
        # search domains are constructed in a list of tuples. It makes a search domaind depend of parameters
        # search domain is builted for get account.move.lines that match with final search domain.
        #        
        # *******************************BUILD SEARCH DOMAINS***************************#
        # if filter_data and filter_type are None (they don't have data) and fiscal_year doesn't exist
        # the method takes accounts that match with target_move parameter.
        #===============================================================================
 
        #********journal_ids ******#
        #journal_ids is a browse record (create a list with only ids)
        list_journal = []
        for journal in journal_ids:
            list_journal.append(journal.id)        
       
        domain = ('journal_id', 'in', list_journal)
        list_tuples.append(domain)        
        
        #********target_mvove ******#
        if not target_move == 'all':
            domain = ('move_id.state', '=', target_move)
            list_tuples.append(domain)        
        
        #********Filter by date, period or filter_type = '' *********#
        if filter_type == 'filter_date':
            if filter_data[0] is None: #it takes only final_date.
                date_stop = filter_data[1]
                domain = ('date', '<=', date_stop)
                list_tuples.append(domain)
            else:
                domain_start_date = ('date', '>=', filter_data[0])
                domain_stop_date = ('date', '<=', filter_data[1])
                list_tuples.append(domain_start_date)
                list_tuples.append(domain_stop_date)                

        elif filter_type == 'filter_period':
            period_domain_list = []
            date_stop = ('date_stop', '<=', filter_data[1].date_stop)
            period_domain_list.append(date_stop)
            #It is considered fiscal_year and special_period.
            if fiscalyear:
                fiscal_year = ('fiscalyear_id', '=', fiscalyear.id)
                period_domain_list.append(fiscal_year)
            if special_period == False:
                special = ('special', '=', False)
            else:
                special = ('special', '=', True)
            period_domain_list.append(special)
            
            if filter_data[0]: 
                #This case is for reports that take initial_period or initial_date as parameter
                date_start = ('date_start', '>=', filter_data[0].date_start)
                period_domain_list.append(date_start)
            
            #In final search domain, it takes fiscal_year, special periods, and start/end period
            periods_ids = self.pool.get('account.period').search(cr, uid,period_domain_list, context=context)
                
            #Get periods with previous ids.
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
        
        #If filter doesn't exist, but fiscal_year exist, get periods that match with fiscal_year
        #special_period parameter indicates that special periods are considered.
        elif filter_type == '' and fiscalyear:
            if special_period is True:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', True),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            else:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', False),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
            
        #********PASS ALL THE PARMETERS IN LIST_TUPLES AND CALL SEARCH METHOD*********************#
        move_line_ids = move_line_obj.search(cr, uid, list_tuples, order = order_by, context=context)
        move_lines = move_line_ids and move_line_obj.browse(cr, uid, move_line_ids, context=context) or []
        
        return move_lines
    
    #Include option for historic strict
    def get_move_lines_partner(self, cr, uid, partner_ids, account_ids, filter_type='', filter_data=None, fiscalyear=None, target_move='all', unreconcile = False, historic_strict = False, special_period = False, order_by = None, context=None):
        
        ''' 
        Get the move lines of the journal provided and filtered.
        
        Arguments:
        'partner_ids': List of partner ids.
        'filter_type': Filter used, possibles values: 'filter_date', 'filter_period' or ''.
        'filter_data': If filter is by date then filter_data is a list of strings with the initial date and the ending date, if filter is by period then
                       filter_data is a list of browse record with the initial period and the ending period.
        'fiscalyear':  Browse record of the fiscal year selected.
        'target_move': Target moves of the report, possibles values: 'all' or 'posted'.
        'order_by': Used to the lines return order by specific order. asc or desc are the accepted words. Also, we can specified which field is going to be used
         
        '''
        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = []
        list_tuples = []
       
        #===============================================================================
        # search domains are constructed in a list of tuples. It makes a search domaind depend of parameters
        # search domain is builted for get account.move.lines that match with final search domain.
        #        
        # *******************************BUILD SEARCH DOMAINS***************************#
        # if filter_data and filter_type are None (they don't have data) and fiscal_year doesn't exist
        # the method takes accounts that match with target_move parameter.
        #===============================================================================
 
        #********partner_ids ******#
        domain = ('partner_id', 'in', partner_ids)
        list_tuples.append(domain)        
        
        #*******account_ids ******#
        domain = ('account_id', 'in', account_ids)
        list_tuples.append(domain) 
        
        #********target_mvove ******#
        if not target_move == 'all':
            domain = ('move_id.state', '=', target_move)
            list_tuples.append(domain)        
        
        #********Filter by date, period or filter_type = '' *********#
        if filter_type == 'filter_date':
            if filter_data[0] is None: #it takes only final_date.
                date_stop = filter_data[1]
                domain = ('date', '<=', date_stop)
                list_tuples.append(domain)
            else:
                domain_start_date = ('date', '>=', filter_data[0])
                domain_stop_date = ('date', '<=', filter_data[1])
                list_tuples.append(domain_start_date)
                list_tuples.append(domain_stop_date)                

        elif filter_type == 'filter_period':
            period_domain_list = []
            date_stop = ('date_stop', '<=', filter_data[1].date_stop)
            period_domain_list.append(date_stop)
            #It is considered fiscal_year and special_period.
            if fiscalyear:
                fiscal_year = ('fiscalyear_id', '=', fiscalyear.id)
                period_domain_list.append(fiscal_year)
            if special_period == False:
                special = ('special', '=', False)
            else:
                special = ('special', '=', True)
            period_domain_list.append(special)
            
            if filter_data[0]: 
                #This case is for reports that take initial_period or initial_date as parameter
                date_start = ('date_start', '>=', filter_data[0].date_start)
                period_domain_list.append(date_start)
            
            #In final search domain, it takes fiscal_year, special periods, and start/end period
            periods_ids = self.pool.get('account.period').search(cr, uid,period_domain_list, context=context)
                
            #Get periods with previous ids.
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
        
        #If filter doesn't exist, but fiscal_year exist, get periods that match with fiscal_year
        #special_period parameter indicates that special periods are considered.
        elif filter_type == '' and fiscalyear:
            if special_period is True:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', True),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            else:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', False),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
            
        #********PASS ALL THE PARMETERS IN LIST_TUPLES AND CALL SEARCH METHOD*********************#
        #move_line_ids = move_line_obj.search(cr, uid, list_tuples, order = order_by, context=context)
        #move_lines = move_line_ids and move_line_obj.browse(cr, uid, move_line_ids, context=context) or []
        
        #===========================================================================================#
        if unreconcile == False:
            move_line_ids = move_line_obj.search(cr, uid, list_tuples,order = order_by,context=context)
                
        else:
            #list_tuples + [domain_unreconciled] -> With this syntax doesn't change the variable
            #list_tuples, the + makes a complete list with domain_unreconciled. Add [] for make as a format list.
            
            #First, move line ids without reconcile_id (without conciliation)
            domain_unreconciled = ('reconcile_id', '=', None)      
            unreconciled_move_line_ids = move_line_obj.search(cr, uid, list_tuples + [domain_unreconciled], context=context)
            
            #historict_strict = If user needs a historic strict (this option obtains all move lines
            #without conciliation to the date requested in report.)  
            if historic_strict == False:
                move_line_ids = unreconciled_move_line_ids
                
            #Mark historic_strict as True
            else: 
                #Get maximal conciliation date to get move lines.
                if filter_type == 'filter_date':
                    #maximal conciliation date is date selected
                    max_reconciled_date = filter_data[1]    
                elif filter_type == 'filter_period':
                    #maximal conciliation date is final date of selected period
                    max_reconciled_date = filter_data[1].date_stop
                elif fiscalyear:
                    #If only fiscalyear exists, it takes end_date as maximal conciliation date
                    max_reconciled_date = fiscalyear.date_end
                else:
                    max_reconciled_date = False
                
                #If maximal date exists, get move lines without conciliation
                #It is to compare unreconciled lines vrs reconciled lines.
                #If any date_crete in unreconciled lines is more than maximal date of conciliation,
                # add in list of unreconciled lines.
                if max_reconciled_date:
                    domain_reconciled = ('reconcile_id', '<>', None)  
                    reconciled_move_line_ids = move_line_obj.search(cr, uid, list_tuples + [domain_reconciled], context=context)
                    reconciled_move_lines = move_line_obj.browse(cr, uid, reconciled_move_line_ids, context=context)
                    for line in reconciled_move_lines:
                        if line.reconcile_id:
                            if line.reconcile_id.create_date > max_reconciled_date:
                                unreconciled_move_line_ids.append(line.id)
                    
                move_line_ids = unreconciled_move_line_ids
        
        move_lines = move_line_ids and move_line_obj.browse(cr, uid, move_line_ids, context=context) or []
        
        return move_lines