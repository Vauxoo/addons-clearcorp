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

import time
import pooler
from report import report_sxw
import locale
from openerp.tools.translate import _

from openerp.addons.account_report_lib.account_report_base import accountReportbase #Library Base

class Parser(accountReportbase):
    
    def __init__(self, cr, uid, name, context):
        
        super(Parser, self).__init__(cr, uid, name, context=context)
       
        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'context':context,
            'storage':{},
            'cumul_balance':None,
            #=======Display data
            'get_display_sort_selection': self.get_display_sort_selection,
            'get_partner_name': self.get_partner_name,
            'get_currency_name':self.get_currency_name,
            'display_partner':self.display_partner,
            #=======Built data and results
            'built_result': self.built_result,       
            'get_amounts_move_line':self.get_amounts_move_line,
            'compute_inicial_balance':self.compute_inicial_balance,
            'compute_cum_balance': self.compute_cum_balance,
            'result_lines':self.result_lines,
            'get_check_open_balance': self.get_check_open_balance,
            #=====Get and set data
            'get_initial_balance': self.get_initial_balance,            
            'reset_values':self.reset_values,
            'total_by_type': self.total_by_type,     
            'get_final_cumul_balance': self.get_final_cumul_balance,
            'get_move_lines_per_partner': self.get_move_lines_per_partner,
            'partner_in_currency': self.partner_in_currency,
        })
        
    #==========================================================================
    
    #=== Display account_type      
    def get_display_sort_selection(self, data):
        val = self._get_form_param('account_type', data)
        if val == 'customer':
            return _('Receivable accounts')
        elif val == 'supplier':
            return _('Payable accounts')
        elif val == 'customer_supplier':
            return _('Payable and Receivable accounts')
        else:
            return val
    
    #==== Parameters: Return all parameters have been selected in wizard
    def built_parameters(self, cr, uid, data):
        filter_data = []
        partner_ids = []
        
        #== Filter type
        filter_type = self.get_filter(data)        
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
    
        #===Fiscal year
        fiscalyear = self.get_fiscalyear(data)
        #===Target_move
        target_move = self.get_target_move(data)
        #===Historic Strict
        historic_strict = self.get_historic_strict(data)
        #===Partner
        partner_list = self.get_partner_ids(data)
        #if partner_ids is not false, it's means that at least a partner has been
        #selected in wizard. If it's false, we take in account all partners
        if partner_list:
            for partner in partner_list:
                partner_ids.append(partner.id)
        else:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [], order='name ASC')
        
        return filter_type, filter_data, fiscalyear, target_move, partner_ids, historic_strict
    #==========================================================================
    
    #1. Get all account that match with account_type selected.
    def get_account_list(self, cr, uid, data):
        account_type = self._get_form_param('account_type', data)
        domain = []
        
        if account_type == 'customer':
            domain.append('receivable')
        if account_type == 'supplier':
            domain.append('payable')
        if account_type == 'customer_supplier':
            domain.append('receivable')
            domain.append('payable')
        
        account_ids = self.pool.get('account.account').search(cr, uid, [('type', 'in', domain)])
        dict_update = {'account_ids':account_ids}
        self.localcontext['storage'].update(dict_update)
        
        return account_ids
    
    #2. Get all account_move_lines that match with previous account.
    def get_move_lines(self, cr, uid, data):
        
        account_library = self.pool.get('account.webkit.report.library')
        
        filter_type, filter_data, fiscalyear, target_move, partner_ids, historic_strict = self.built_parameters(cr, uid, data)
        account_ids = self.get_account_list(cr, uid, data)
        
        #If in wizard at least one partner is selected, filter move lines by partner
        if partner_ids:
            move_lines = account_library.get_move_lines_partner(cr,1,partner_ids, account_ids,
                                                            filter_type=filter_type, 
                                                            filter_data=filter_data, 
                                                            fiscalyear=fiscalyear, 
                                                            target_move=target_move,
                                                            unreconcile = True,
                                                            historic_strict=historic_strict,
                                                            order_by='date ASC')
        else:       
            #Return all move lines (With all partners)            
            move_lines = account_library.get_move_lines(cr, 1, partner_ids, account_ids, 
                                                            filter_type=filter_type, 
                                                            filter_data=filter_data, 
                                                            fiscalyear=fiscalyear, 
                                                            target_move=target_move,
                                                            unreconcile = True,
                                                            historic_strict=historic_strict,
                                                            order_by='date ASC')
        return move_lines
    
    #3. Classified the move_lines
    #===========================================================================
    # This method create a dictionary. In each key, it has another dictionary
    # that contains a list of move lines. This structure classified all move
    # lines first by currency and then, by partner 
    #===========================================================================
    
    """    
    For built_result method, the result could be iterated as follow:
        *result is a dictionary of dictionaries
        
        for currency, partners in result.iteritems():
            print currency (in this case, it will display the currency)
            
            for partner, lines in partner.iteritems():
                print partner (in this case, it will partner's name)
                
                for line in lines:
                    print line.name, line.ref ... (lines is a list of move_lines)    
        
        Also, return a list of partners sort by name. This is for show partners sort by name
    """
    def built_result(self, cr, uid, data):
       list_ids = []       
       result = {}
       currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id
       
       #Get move_lines       
       move_lines = self.get_move_lines(cr, uid, data)
        
       #Classified move_lines by currency and partner
       for line in move_lines:
           if not line.currency_id or line.currency_id.name == currency_company.name:
               if currency_company.id not in result.keys():
                   result[currency_company.id] = {}
                
               if not line.partner_id:
                    if 'no_partner' not in result[currency_company.id].keys():
                        result[currency_company.id]['no_partner'] = []
                        #==== ID list (without repeat id)  
                        list_ids.append(0)
                    result[currency_company.id][0].append(line) #zero is key for 'no partner'                    
                    
               else:
                    if line.partner_id.id not in result[currency_company.id].keys():
                        result[currency_company.id][line.partner_id.id] = []
                        #==== ID list (without repeat id)                                  
                        list_ids.append(line.partner_id.id)                         
                    result[currency_company.id][line.partner_id.id].append(line) 
                   
           else:
               if line.currency_id.id not in result.keys():
                   actual_currency = line.currency_id.id
                   result[actual_currency] = {}                   
                
               if not line.partner_id:
                    if 'no_partner' not in result[actual_currency].keys():
                        result[actual_currency][0] = []
                        #==== ID list (without repeat id) 
                        list_ids.append(0)
                    result[actual_currency][0].append(line)
                    
               else:
                    if line.partner_id.id not in result[actual_currency].keys():
                        result[actual_currency][line.partner_id.id] = []
                        #==== ID list (without repeat id) 
                        list_ids.append(line.partner_id.id)
                    result[actual_currency][line.partner_id.id].append(line)
        
       #Sort by name (alphabetically). In aeroo template iterate in browse
       #record that it's already sort. This method return the dictionary with
       #move_lines and a list of partners sorted. (ids)
       partner_ids_order = self.pool.get('res.partner').search(cr, uid, [('id','in', list_ids)], order='name ASC')
                        
       return result, partner_ids_order
   
    #4. Get amounts for each move_line
    #===========================================================================
    # Return a dictionary, where the key is move_line id and it contains another  
    # dictionary with 6 values: Invoices, voucher, credit, debit, manual 
    # and balance.
    #===========================================================================
    def get_amounts_move_line(self,cr, uid, move_lines, currency_id):
        
        company_currency = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id.id
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        res = {}
        values = {'invoice': 0.0, 'c_d_notes':0.0, 'payment':0.0, 'manual':0.0}
       
        for line in move_lines:       
            #Reset values
            values = {'invoice': 0.0, 'c_d_notes':0.0, 'payment':0.0, 'manual':0.0}
            res[line.id] = values
            
            #Amount
            if currency_id != company_currency:
                amount = line.amount_currency
            else:
                if line.debit > 0.0:
                    amount = line.debit 
                elif line.credit > 0.0: 
                    amount = line.credit * -1
            
            #===================================================================
            # CLASIFITED AMOUNT 
            # Each line divide its amount in five columns. Only one of them
            # has a value.
            #===================================================================
            
            #=== Invoice
            invoice_id = invoice_obj.search(cr, uid, [('move_id', '=', line.move_id.id)], limit=1)
            invoices = invoice_obj.browse(cr, uid, invoice_id, context=None)
            
            #=== Voucher
            voucher_id = voucher_obj.search(cr, uid, [('move_id', '=', line.move_id.id)], limit=1)
            vouchers = voucher_obj.browse(cr, uid, voucher_id, context=None)
            
            # Invoices
            if invoices:
                for invoice in invoices:
                    if invoice.type == 'out_invoice': # Customer Invoice 
                       res[line.id]['invoice'] = amount
                    elif invoice.type == 'in_invoice': # Supplier Invoice
                        res[line.id]['invoice'] = amount
                    elif invoice.type == 'in_refund' or invoice.type == 'out_refund': # Debit or Credit Note
                        res[line.id]['c_d_notes'] = amount
            
            # Voucher
            elif vouchers:
                for voucher in vouchers:
                    if voucher.type == 'payment': # Payment
                        res[line.id]['payment'] = amount
                    elif voucher.type == 'sale': # Invoice
                        res[line.id]['invoice'] = amount
                    elif voucher.type == 'receipt': # Payment
                        res[line.id]['payment'] = amount
            
            # Manual Move
            else:
                res[line.id]['manual'] = amount

        return res
        
    #5. Create a method that compute initial_balance by partner
    """
        @param partner_id: integer, a partner id  
        @param currency_id: integer, a current currency_id
    """
    def compute_inicial_balance(self, cr, uid, partner_id, currency_id, data):
        result = {}
        params = []
        #Set value in localcontext
        self.localcontext['cumul_balance'] = {}  
        
        #===Parameters
        fiscalyear_id = self.get_fiscalyear(data)
        filter_type = self.get_filter(data)
        account_ids = self.get_data_template('account_ids')
        user = self.pool.get('res.users').browse(cr, uid, uid,context=None)

        #if filter_type == period, get all periods before period_start selected 
        if filter_type == 'filter_period':
            start_period = self.get_start_period(data) #return the period object
            period_ids = self.pool.get('account.period').search(cr, uid,[('date_start', '<', start_period.date_start),('fiscalyear_id','=', fiscalyear_id.id)])
            
            #Add account and reconcile
            where_clause = "reconcile_id is NULL " + "AND account_id in %s "
            params.append(tuple(account_ids))
            
            #Add partners
            where_clause += "AND partner_id = %s "
            params.append(tuple([partner_id]))
                
            #Period
            if period_ids:                
                where_clause += "AND period_id in %s "
                params.append(tuple(period_ids))
                
            #Currency
            if currency_id == user.company_id.currency_id.id:
                where_clause += "AND (currency_id is NULL OR currency_id = %s) "
                params.append(currency_id)
                sum_str = " sum(debit-credit) "
            else:
                where_clause += "AND currency_id = %s "
                sum_str = " sum(amount_currency) "
                params.append(currency_id)
                
            sql=("SELECT partner_id as partner,"+ sum_str + "as initial_balance "
                 "FROM account_move_line "
                 "WHERE " + where_clause + "GROUP BY partner_id")
            
        #if filter_type == date, get take in account date start selected
        else:
            date = self.get_date_from(data)
            
            #Add account and reconcile
            where_clause = "date < %s "+" AND reconcile_id is NULL " + "AND account_id in %s "
            params.append(date)
            params.append(tuple(account_ids))
            
            #Add partners
            where_clause += "AND partner_id = %s "
            params.append(tuple([partner_id]))
            
             #Currency
            if currency_id == user.company_id.currency_id.id:
                where_clause += "AND (currency_id is NULL OR currency_id = %s) "
                params.append(currency_id)
                sum_str = " sum(debit-credit) "
            else:
                where_clause += "AND currency_id = %s "
                sum_str = " sum(amount_currency) "
                params.append(currency_id)
            
            sql=("SELECT partner_id as partner," +sum_str+ "as initial_balance "
                     "FROM account_move_line "
                     "WHERE " + where_clause + "GROUP BY partner_id")
        
        param_tuple = tuple(params)
        self.cursor.execute(sql, param_tuple)
        
        #if it exists lines, built a new dictionary, where the key is the partner with initial_balance
        res = self.cursor.dictfetchall()
        
        if res:
            for dict in res:
                result[dict['partner']] = dict['initial_balance']
                #set this result as the first amount of initial balance
                self.localcontext['cumul_balance'][dict['partner']] = result[dict['partner']]
        else:
            result[partner_id] = 0.0                                  
            self.localcontext['cumul_balance'][partner_id] = 0.0

        return result    
     
    """
        Some partners don't appear in list because don't have move lines. 
        But, some partners have balance without lines. That case is when 
        the partner doesn't have any open invoices for selected period, but
        for previous periods if partner has a open balance, it will be print
        only the open balance.
        
        structure:
            result['partner'] = {'currency_1': balance, 'currency_2': balance ...} active currencies 
                         
    """
    def get_check_open_balance(self, cr, uid, data):   
        result = {}       
        active_curency_ids = self.pool.get('res.currency').search(cr, uid, [('active','=',True)], context=None)
        main_dict = self.get_data_template('result') #main dict
        partners = self.set_partners(cr, uid, data)
        
        for partner in partners:
            result[partner] = {}
            balance = {}
            for currency in active_curency_ids:
                if main_dict:
                    if currency in main_dict.keys():
                        if partner not in main_dict[currency].keys():                            
                            res = self.compute_inicial_balance(cr, uid, partner, currency, data)
                            balance[currency] = res[partner]
                else:
                    res = self.compute_inicial_balance(cr, uid, partner, currency, data)
                    balance[currency] = res[partner] 
            
            result[partner] = balance
                    
        dict_update = {'open_balance': result}        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #==========================================================================
    
    #===========Methods for compute final balances
    #Store acumulated balance for each partner
    def compute_cum_balance(self, partner, res):
        # The first time, cumul_balance takes balance for partner, 
        # then, get this value and compute with values for each line.
        cumul_balance = self.localcontext['cumul_balance'][partner] 
        cumul_balance = cumul_balance + res['invoice'] + res['c_d_notes'] + res['payment'] + res['manual']
        self.localcontext['cumul_balance'][partner] = cumul_balance
        
        return cumul_balance
    
    #Return the total balance for each amount. Compute at the end of each partner
    def total_by_type(self, move_lines):   
               
        final = {'invoice' : 0.0, 'c_d_notes': 0.0, 'payment': 0.0, 'manual': 0.0,}
        
        #Dictionary with final results
        result = self.get_data_template('amount_per_line')
        
        for line in move_lines:
            final['invoice'] += result[line.id]['invoice']
            final['c_d_notes'] += result[line.id]['c_d_notes']
            final['payment'] += result[line.id]['payment']
            final['manual'] += result[line.id]['manual']
        
        return final   
          
    #=========== Methods to get and set data    
    #set data to use in odt template. 
    def set_data_template(self, cr, uid, data):        
        result, partner_ids_order = self.built_result(cr, uid, data)
        dict_update = {'result': result, 'partners': partner_ids_order}        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #Return a dictionary with all values for a move_lines list
    def result_lines(self, cr, uid, move_lines, currency_id):
        amount_per_line = self.get_amounts_move_line(cr, uid, move_lines, currency_id)        
        dict_update = {'amount_per_line': amount_per_line}
        self.localcontext['storage'].update(dict_update)
        return False
    
    #Reset cumul_balance for each partner
    def reset_values(self):
        self.localcontext['cumul_balance'] = None
            
    #Return cumul_balance for a specific partner
    def get_final_cumul_balance(self, partner):
        return self.localcontext['cumul_balance'][partner]

    #Return initial balance for a specific partner.
    """@param partner: partner is an id (integer). It's comming for the odt template """
    def get_initial_balance(self, cr, uid, partner, currency, data):
        self.compute_inicial_balance(cr, uid, partner, currency, data)
        return self.localcontext['cumul_balance'][partner]  
    
    #Return move_lines for a specific partner
    def get_move_lines_per_partner(self, currency, partner):
        if partner in self.localcontext['storage']['result'][currency].keys():
            return self.localcontext['storage']['result'][currency][partner]
        else:
            return []
    
    #Avoid to show partners without lines and partner that doesn't match with 
    #currency
    def partner_in_currency(self, partner,currency):
         if partner in self.localcontext['storage']['result'][currency].keys():
             return True
         else:
             return False
    
    def set_partners(self, cr, uid, data):
        partner_ids = []
        
        #===Partner
        partner_list = self.get_partner_ids(data)
        #if partner_ids is not false, it's means that at least a partner has been
        #selected in wizard. If it's false, we take in account all partners
        if partner_list:
            for partner in partner_list:
                partner_ids.append(partner.id)
        else:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [], order='name ASC')
        
        return partner_ids
    
    #=========Methods for display data 
    #Display name of a specific partner
    def get_partner_name(self, cr, uid, partner_id):        
        if partner_id != 0:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)                  
            if partner.ref and partner.name:
                return partner.name + ' - REF: ' + partner.ref 
            else:
                return partner.name
        else:
            return 'No partner'
    
    #Display the currency name    
    def get_currency_name(self, cr, uid, currency_id):
        return self.pool.get('res.currency').browse(cr, uid, currency_id).name
    
    #Display partner if it has a open balances without open invoices
    def display_partner(self, dict):
       value = 0.0
       display = False
       
       for currency, value in dict.iteritems():
           if value != 0: #if any currency has a value, the partner will be print in report
               display = True
       return display    
