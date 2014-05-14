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

from tools.translate import _
import pooler

from openerp.addons.account_report_lib.account_report_base import accountReportbase

class Parser(accountReportbase):

    def __init__(self, cursor, uid, name, context):
        super(Parser, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr   
        
        self.localcontext.update({ 
            'storage':{},
            'cumul_balance': 0.0,
            'get_bank_account': self.get_bank_account,
            'get_period': self.get_period, 
            'display_account_name': self.display_account_name,
            'account_has_move_lines': self.account_has_move_lines,
            'messages': self.messages,
            'return_balance_account':self.return_balance_account,
            'display_symbol_account': self.display_symbol_account, 
            'update_cumul_balance': self.update_cumul_balance,
            'reset_data': self.reset_data,
            'get_cumul_balance':self.get_cumul_balance,
        })  
        
    #=================== DISPLAY DATA ===================================
    def messages(self):
        message = _("For this account, doesn't exist move lines")
        return message
    
    def account_has_move_lines(self, account_id):
        if account_id in self.localcontext['storage']['result'].keys():
            if len(self.localcontext['storage']['result'][account_id]) > 0:
                return True
            else:
                return False
    
    def display_account_name(self, data, account_id):
        str_name = ''
        bank_account = self.get_bank_account(data)
        
        if bank_account.default_credit_account_id  and bank_account.default_debit_account_id:
            if bank_account.default_credit_account_id.id == bank_account.default_debit_account_id.id: 
                str_name = bank_account.default_credit_account_id.code + ' - ' + bank_account.default_credit_account_id.name + ' - ' + bank_account.default_credit_account_id.currency_id.name
        
            else:
                if bank_account.default_credit_account_id:
                    if bank_account.default_credit_account_id.id == account_id:
                        str_name = _('Default credit account: ') + bank_account.default_credit_account_id.code + ' - ' + bank_account.default_credit_account_id.name + ' - ' + bank_account.default_credit_account_id.currency_id.name
                
                elif bank_account.default_debit_account_id:
                    if bank_account.default_debit_account_id.id == account_id:
                        str_name = _('Default debit account: ') + bank_account.default_debit_account_id.code + ' - ' + bank_account.default_debit_account_id.name + ' - ' + bank_account.default_debit_account_id.currency_id.name
        
        else:
             if bank_account.default_credit_account_id:
                 if bank_account.default_credit_account_id.id == account_id:
                     str_name = _('Default credit account: ') + bank_account.default_credit_account_id.code + ' - ' + bank_account.default_credit_account_id.name + ' - ' + bank_account.default_credit_account_id.currency_id.name
                
             elif bank_account.default_debit_account_id:
                 if bank_account.default_debit_account_id.id == account_id:
                     str_name = _('Default debit account: ') + bank_account.default_debit_account_id.code + ' - ' + bank_account.default_debit_account_id.name + ' - ' + bank_account.default_debit_account_id.currency_id.name
        
        return str_name
    
    def display_symbol_account(self, account_id):
        account = self.pool.get('account.account').browse(self.cr, self.uid, account_id)
        if account.currency_id:
            return account.currency_id.symbol
        else:
            return ''
    
    #=============== SET AND GET DATA ====================================#
    def reset_data(self):
        self.localcontext['storage']['cumul_balance'] = 0.0
        return False
        
    def get_cumul_balance(self):
        return self.localcontext['storage']['cumul_balance']
    
    def get_bank_account(self, data):
        return self._get_info(data, 'res_partner_bank_ids', 'res.partner.bank')

    def get_period(self, data):
        return self._get_info(data, 'period_ids', 'account.period')  
    
    def get_currency_company(self):
        return self.pool.get('res.users').browse(self.cr, self.uid, [self.uid])[0].company_id.currency_id
    
    def different_currency(self, currency_id):
        currency_company = self.get_currency_company()        
        if currency_company != currency_id:
            return True
        else:
            return False

    #Change cumul_balance when changes the line
    def update_cumul_balance(self, line):
        cumul_balance = self.localcontext['storage']['cumul_balance']        
        if line.currency_id:
            if line.currency_id.id == self.get_currency_company():
                cumul_balance = self.localcontext['storage']['cumul_balance'] + line.debit - line.credit
                dict_update = {'cumul_balance': cumul_balance}
                self.localcontext['storage'].update(dict_update)            
            else:
                cumul_balance = self.localcontext['storage']['cumul_balance'] + line.amount_currency
                dict_update = {'cumul_balance': cumul_balance}
                self.localcontext['storage'].update(dict_update)                

        return cumul_balance
                
    def set_data_template(self, data):        
        #Main dictionary
        res = self.classified_move_lines(data)     
        dict_update = {'result': res,} 
        self.localcontext['storage'].update(dict_update)
        return False      
    
    def return_balance_account(self, data, account_id):
        #Depends of account currency, return balance or foreign balance
        balance = self.get_initial_balance(data, account_id)            
        account = self.pool.get('account.account').browse(self.cr, self.uid, account_id)
        currency_company = self.get_currency_company()
        
        if account.currency_id:
            if account.currency_id == currency_company:
                #initialize cum_balance 
                dict_update = {'cumul_balance': balance[account_id]['balance']}
                self.localcontext['storage'].update(dict_update)
                return balance[account_id]['balance']
            else:
                #initialize cum_balance
                dict_update = {'cumul_balance': balance[account_id]['foreign_balance']}
                self.localcontext['storage'].update(dict_update)
                return balance[account_id]['foreign_balance']
            
    #=====================================================================#
    
    #===================================================================
    # Find move_lines that match with default_credit_account_id or 
    # default_debit_account_id, status = valid and period is the 
    # same with selected in wizard
    #===================================================================                        
    def process_move_lines(self, data):
        account_ids = []
        
        period = self.get_period(data)
        bank_account = self.get_bank_account(data)
        
        if bank_account.default_credit_account_id and bank_account.default_debit_account_id:
            if bank_account.default_credit_account_id.id == bank_account.default_debit_account_id.id:
                account_ids.append(bank_account.default_debit_account_id.id)            
            else:    
                account_ids.append(bank_account.default_credit_account_id.id)
                account_ids.append(bank_account.default_debit_account_id.id)
        
        elif bank_account.default_credit_account_id:
            account_ids.append(bank_account.default_credit_account_id.id)
        
        elif bank_account.default_debit_account_id:
            account_ids.append(bank_account.default_debit_account_id.id)        
            
        move_lines_ids = self.pool.get('account.move.line').search(self.cr, self.uid, [('account_id','in',account_ids),('state', '=', 'valid'),('period_id','=',period.id)])
        move_lines = self.pool.get('account.move.line').browse(self.cr, self.uid, move_lines_ids)
        
        return move_lines
    
    #=======================================================================
    # Create a dictionary where account is key and each of them have a 
    # move lines list associated
    #=======================================================================
    def classified_move_lines(self, data):
        res = {}
        
        #Get move_lines 
        move_lines = self.process_move_lines(data)
        
        for line in move_lines:
            #lines must have a account if they are included in list
            #It is not necessary included a check with account
            if line.account_id.id not in res:
                res[line.account_id.id] = []
            res[line.account_id.id].append(line)
        
        return res
    
    #=======================================================================
    # Create a dictionary where account is key and each of them have a 
    # balance associated (initial balance)
    #=======================================================================
    def get_initial_balance(self, data, account_id):
        account_balance = 0.0
        library_obj = self.pool.get('account.webkit.report.library')
        
        fiscal_year = self.get_fiscalyear(data)            
        account = self.pool.get('account.account').browse(self.cr, self.uid, account_id)
        period = self.get_period(data)
        currency_company = self.get_currency_company()
        
        #Get initial balance with previous period for period selected
        previous_period = self.pool.get('account.period').get_start_previous_period(self.cr, self.uid, start_period=period, fiscal_year=fiscal_year)
        
        if account.currency_id:
            #Compare currency, if account is different than currency company, get foreign_balance 
            if account.currency_id.id == currency_company:
                account_balance = library_obj.get_account_balance(self.cr, self.uid, 
                                                                      [account_id], 
                                                                      ['balance'], 
                                                                      initial_balance=True,
                                                                      fiscal_year_id=fiscal_year.id,                                                                                
                                                                      start_period_id=previous_period, 
                                                                      end_period_id=previous_period, 
                                                                      filter_type='filter_period')
            else:
                account_balance = library_obj.get_account_balance(self.cr, self.uid, 
                                                                      [account_id], 
                                                                      ['foreign_balance'], 
                                                                      initial_balance=True,
                                                                      fiscal_year_id=fiscal_year.id,                                                                                
                                                                      start_period_id=previous_period, 
                                                                      end_period_id=previous_period, 
                                                                       filter_type='filter_period')
        else:
            account_balance = 0.0   
       
        return account_balance