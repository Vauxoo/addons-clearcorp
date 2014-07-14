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
from tools.translate import _
import pooler

from openerp.addons.account_report_lib.account_report_base import accountReportbase #Library Base

class Parser(accountReportbase):
     
    def __init__(self, cr, uid, name, context):        
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        
        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'context':context,
            'storage':{},
            'set_data_template': self.set_data_template,
            'get_print_name': self.get_print_name,
            'partner_in_dictionary':self.partner_in_dictionary,
            'get_data_by_partner':self.get_data_by_partner,
            'define_debit_credit':self.define_debit_credit,
            'error_message': self.error_message,
            'compute_total_debit_credit':self.compute_total_debit_credit,
            'compute_total_currency_company':self.compute_total_currency_company,
            'get_company_user':self.get_company_user,
            'get_currency_company_user_name': self.get_currency_company_user_name,
            'compute_exchange_rate':self.compute_exchange_rate,
        })
        
    """ 
        1. Get account_move_lines related with partner and classify by type  
                
        #===========================================================================
        # This method create a dictionary. In each key, it has another dictionary
        # that contains a list of move lines. This structure classified all move
        # lines first by currency and then, by partner 
        #===========================================================================  
        
        For built_result method, the result could be iterated as follow:
        *result is a dictionary of dictionaries
        
        for partner, currency in result.iteritems():
            print partner (in this case, it will display the partner's name)
            
            for currency, type in partner.iteritems():
                print partner (in this case, it will currency's name)
                
                for type, lines in currency.iteritems():
                    print type (in this case, it will type's name, it would be Receivable or Payable

                    for line in lines:
                        print line.name, line.ref ... (lines is a list of move_lines)    
        
        Also, return a list of partners sort by name. This is for show partners sort by name
        
        @param partner_list: It can be one partner o a list of them. The user
        would select one or many in form list view.
    """
        
    def get_account_move_lines(self, cr, uid, objects, context=None):
       move_line_obj = self.pool.get('account.move.line')
        
       partner_ids = []
       move_lines_ids = []
       res = {}
       
       currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id
        
       """ 1. Extract partner's id and then search move lines."""        
       for partner in objects:
           partner_ids.append(partner.id)
        
       """2. Search move lines that match with this partners """
       move_lines_ids = move_line_obj.search(cr, uid, [('partner_id','in', partner_ids),('reconcile_id','=',False),('account_id.type','in',['payable','receivable'])], order = 'date ASC')
       move_lines = move_line_obj.browse(cr, uid, move_lines_ids)
        
       """ 3. Classified move_lines by partner and account_type """
     #Classified move_lines by currency and partner
       for line in move_lines:
           if line.partner_id.id not in res.keys():
               res[line.partner_id.id] = {}
            
           if line.account_id.type not in res[line.partner_id.id].keys():
               res[line.partner_id.id][line.account_id.type] = {}
               
           if not line.currency_id:
               if currency_company.id not in res[line.partner_id.id][line.account_id.type].keys():
                   res[line.partner_id.id][line.account_id.type][currency_company.id] = []
               res[line.partner_id.id][line.account_id.type][currency_company.id].append(line)                

           else:
               if line.currency_id.id not in res[line.partner_id.id][line.account_id.type].keys():                   
                   res[line.partner_id.id][line.account_id.type][line.currency_id.id] = []
               res[line.partner_id.id][line.account_id.type][line.currency_id.id].append(line)
             
       #Sort by name (alphabetically). In aeroo template iterate in browse
       #record that it's already sort. This method return the dictionary with
       #move_lines and a list of partners sorted. (ids)
       partner_ids_order = self.pool.get('res.partner').search(cr, uid, [('id','in', partner_ids)], order='name ASC')
                        
       return res, partner_ids_order
    
    """ 
        2. Return the value for debit or credit for each line
        @param line: A account_move_line line object
    """   
    def define_debit_credit(self, cr, uid, line):
        debit = 0.0
        credit = 0.0
        
        res = {'debit':debit, 'credit':credit}
        
        currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id
        
        #Use amount_currency in this case
        if (line.currency_id != currency_company) and line.currency_id:
            if line.amount_currency > 0:
                debit = line.amount_currency
            elif line.amount_currency < 0:
                credit = line.amount_currency * -1
            res.update({'debit':debit, 'credit':credit})            
        
        #currency_id = False, company_id currency
        else:
            res.update({'debit':line.debit, 'credit':line.credit})
        
        return res
    """ 
        3. Compute debit and credit column for each lines block
        @param lines: A list of lines.
    """   
    def compute_total_debit_credit(self, cr, uid, lines):
       debit = 0.0
       credit = 0.0
        
       res = {'debit':debit, 'credit':credit}
        
       currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id
        
       for line in lines:
           #Use amount_currency in this case
           if (line.currency_id != currency_company) and line.currency_id:
               if line.amount_currency > 0:
                   debit += line.amount_currency
               elif line.amount_currency < 0:
                   credit += line.amount_currency * -1
               
           #currency_id = False, company_id currency
           else:
               debit += line.debit
               credit += line.credit
        
       res.update({'debit':debit, 'credit':credit})
       return res
    
    """
        Compute total by type 
        @param currency: A dictionary, it contains the type and amount per type
    """
    def compute_total_currency_company(self, cr, uid, partner,type):        
       debit = 0.0
       credit = 0.0
       amount = 0.0
        
       currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id.id
       
       type_dict = self.get_data_by_partner(partner)[type]
       for currency, lines in type_dict.iteritems():
           result = self.compute_total_debit_credit(cr, uid, lines)
           
           #Compute all data for each type.
           #If type's currency is different from currency_company
           #the amount must be converted to currency_company
           if currency != currency_company:                   
               amount_to_convert = result['debit'] - result['credit']
               amount += self.currency_convert_amount(cr, uid, currency, currency_company, amount_to_convert)
           
           else:
               subtotal = result['debit'] - result['credit']
               amount += subtotal
        
       return amount
   
    def compute_exchange_rate(self, cr, uid, partner,type, context):        
       debit = 0.0
       credit = 0.0
       amount = 0.0
        
       currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id
       
       type_dict = self.get_data_by_partner(partner)[type]
       for currency, lines in type_dict.iteritems():
          currency_current = self.pool.get('res.currency').browse(cr, uid, currency)
          conversion_rate_str = self.get_conversion_rate(cr, uid, currency_current, currency_company, context)
        
       return conversion_rate_str
       
    #================ AUXILIAR FUNCTIONS =======================================
    """ 
        Get exchange rate for today between currency and company's currency 
        for a specific amount.
        
        @param initial_currency: it must be a currency id
        @param final_currency: it must be a currency id 
        @param amount: amount to convert
    """        
    def currency_convert_amount(self, cr, uid, initial_currency, final_currency, amount, context=None):
        res_currency = self.pool.get('res.currency')        
        exchange_rate = res_currency.compute(cr, uid, initial_currency, final_currency, amount)
        return exchange_rate
    
    """
        Return a specific name for a id, this method if for print the name
        in aeroo template
        @param id: id . It must be a number
        @param type: the type of register that matches with the id. A model for
                     OpenERP system
        @param type_name: Specific parameter for account's type. In this case,
                          it could be receivable or payable
    """
    def get_print_name(self, cr, uid, id, type='', type_name='', context=None):
        
        if type == 'partner':
            partner = self.pool.get('res.partner').browse(cr, uid, id)
            return partner.name
        
        #for this case, 'id' parameter is a string
        if type == 'account_type':
            if id == 'payable':
                return _('Payable')
            elif id == 'receivable':
                return _('Receivable')
        
        if type == 'currency':
            return self.pool.get('res.currency').browse(cr, uid, id, context=context).name
    
    """ 
        Return a conversion rate for today's date
        @param initial_currency: It must be a browse record
        @param final_currency: It must be a browse record        
    """    
    def get_conversion_rate(self, cr, uid, initial_currency, final_currency, context): 
        res_currency_obj = self.pool.get('res.currency')   
        copy_context = context     
        
        now = time.strftime('%Y-%m-%d')        
        conversion_rate = res_currency_obj.get_exchange_rate(cr, uid, initial_currency, final_currency, now, context=context)
        now = time.strftime('%d-%m-%Y')
        
        conversion_rate_str = now + ' '+ final_currency.symbol + ' ' + str(conversion_rate)
        
        return conversion_rate_str
        
    #================== METHODS TO SET AND GET DATA ===========================#
            
    """ Set data to use in odt template """
    def set_data_template(self, cr, uid, objects):        
        result, partner_ids_order = self.get_account_move_lines(cr, uid, objects,context=None)        
        dict_update = {'result': result, 'partner_ids_order': partner_ids_order,}        
        self.localcontext['storage'].update(dict_update)
        return False
    
    """
        Return a dictionary, with this structure:
        result[account_type][currency] = move_list_lines
    """
    def get_data_by_partner(self, partner_id):
       return self.localcontext['storage']['result'][partner_id]
       
    """
        Avoid to show partners without lines and partner that doesn't match with 
        currency
    """
    def partner_in_dictionary(self, partner):
         if partner in self.localcontext['storage']['result'].keys():
             return True
         else:
             return False
    
    #Error message for report    
    def error_message(self):
        return _("For this partner, doesn't exist payable or receivable pending invoices ")
    
    #Return company for logged user
    def get_currency_company_user_name(self, cr, uid):        
        currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.currency_id.name
        return currency_company
    
    def get_company_user(self, cr, uid):        
        currency_company = self.pool.get('res.users').browse(cr, uid, [uid])[0].company_id.name
        return currency_company