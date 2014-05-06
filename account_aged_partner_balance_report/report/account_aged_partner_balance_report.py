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
from openerp.osv import fields, osv

from openerp.addons.account_report_lib.account_report_base import accountReportbase

class Parser(accountReportbase):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        
        self.localcontext.update({ 
            'cr' : cr,
            'uid': uid,       
            'storage':{},
            'set_data_template': self.set_data_template,
            'set_data_move_lines': self.set_data_move_lines,
            'get_data':self.get_data,   
            'get_data_by_partner':self.get_data_by_partner, 
            'get_period_length': self.get_period_length,
            'get_direction_selection': self.get_direction_selection,
            'display_account_type':self.display_account_type,
            'display_direction_selection': self.display_direction_selection, 
            'display_period_length': self.display_period_length,
            'process_lines_period':self.process_lines_period,
        })
    
    #====Extract data from wizard==============================================    
    def get_period_length(self, data):
        return self._get_form_param('period_length', data)
    
    def get_direction_selection(self, data):
        return self._get_form_param('direction_selection', data)
    
    def get_account_type(self, data):
        return self._get_form_param('account_type', data)
        
    """
        Return a dictionary, with this structure:
        result[account_type][move_list_lines] (a dictionary) 
    """
    def get_data_by_partner(self, partner_id):
       return self.localcontext['storage']['result'][partner_id]
        
    #==========================================================================
    
    #====Display data==========================================================
    def display_account_type(self, data=None, account_type=None): 
        #if it's necessary to display in report's header
        if data:            
            account_type = self.get_account_type(data)            
        
        ##Options for report information (keys are different) 
        if account_type == 'receivable':
            return _('Receivable Accounts')
        elif account_type == 'payable':
            return _('Payable Accounts')
        
        ###Options for header
        if account_type == 'customer':
            return _('Receivable accounts')
        elif account_type == 'supplier':
            return _('Payable accounts')
        elif account_type == 'customer_supplier':
            return _('Payable and Receivable accounts')
        return ''
        
    def display_direction_selection(self, data):
        direction_selection = self.get_direction_selection(data)
                
        if direction_selection == 'past':
            return _('Past')
        elif direction_selection == 'future':
            return _('Future') 
        return ''
    
    def display_period_length(self, data):
        return self.get_period_length(data)     
  
    #===== Set data =========================================================
    #set data to use in odt template. 
    def set_data_template(self, cr, uid, data):        
        result, partner_ids_order   = self.get_data(cr, uid, data)
        dict_update = {'result': result, 'partner_ids_order': partner_ids_order,}        
        self.localcontext['storage'].update(dict_update)
        return False  
    
    def set_data_move_lines(self, data, move_lines):
        #move_lines is a dictionary
        move_lines, partner_total = self.process_lines_period(data, move_lines)
        dict_update = {'move_lines':move_lines, 'partner_total':partner_total}
        self.localcontext['storage'].update(dict_update)
        return False  
        
    #==========================================================================
    
    def get_move_lines(self, data):
        account_account_obj = self.pool.get('account.account')
        account_move_line_obj = self.pool.get('account.move.line')
        account_type_domain = []
        
        #Get parameters
        date_from = str(self.get_date_from(data))
        direction_selection = str(self.get_direction_selection(data))
        account_type = self.get_account_type(data)
        
        if account_type == 'customer':
            account_type_domain.append('receivable')
        if account_type == 'supplier':
            account_type_domain.append('payable')
        if account_type == 'customer_supplier':
            account_type_domain.append('receivable')
            account_type_domain.append('payable')

        #Build domains
        account_account_ids = account_account_obj.search(self.cr, self.uid, [('type', 'in', account_type_domain), ('active','=',True)])
        account_move_line_domain = [('state', '=', 'valid'), ('reconcile_id', '=', False), ('account_id', 'in', account_account_ids)]
        
        #=====Build a account move lines domain
        #Date
        tuple_date = ()        
        if direction_selection == 'past':
            tuple_date = ('date','<=', date_from)
            account_move_line_domain.append(tuple_date)        
        else:
            tuple_date = ('date','>=', date_from)
            account_move_line_domain.append(tuple_date)
        
        #Get move_lines based on previous domain
        account_move_line_ids = account_move_line_obj.search(self.cr, self.uid, account_move_line_domain, order='date_maturity desc')
        account_move_lines = account_move_line_obj.browse(self.cr, self.uid, account_move_line_ids)
        
        return account_move_lines
    
    def get_data(self, cr, uid, data):
       partner_ids = []
       res = {}
              
       """ 1. Extract move lines """
       move_lines = self.get_move_lines(data)
                  
       """ 2. Classified move_lines by partner and account_type """
       for line in move_lines:
           if line.partner_id:
               partner_id = line.partner_id.id
           else:
               partner_id = 0 #key for lines that don't have partner_id
               
           #== Create a list, them order it by name ============
           if partner_id not in partner_ids:
               partner_ids.append(partner_id)
           #====================================================
        
           if partner_id not in res.keys():
               res[partner_id] = {}
            
           if line.account_id.type not in res[partner_id].keys():
               res[line.partner_id.id][line.account_id.type] = []
                              
           res[partner_id][line.account_id.type].append(line)                
             
       #Sort by partner's name (alphabetically) 
       partner_ids_order = self.pool.get('res.partner').search(cr, uid, [('id','in', partner_ids)], order='name ASC')
       partner_list = self.pool.get('res.partner').browse(self.cr, self.uid, partner_ids_order)
       
       return res, partner_list
   
    #Process each column for line.
    def process_lines_period(self, data, move_lines):
       res = {}
       partner_total = 0.0
       result_list = [7]
       
       #Get parameters
       date_from = str(self.get_date_from(data))
       direction_selection = str(self.get_direction_selection(data))        

       for line in move_lines:       
           result_list = map(float, result_list)
           #initialize list
           result_list = [0.0 for i in range(7)]
       
           if not line.date_maturity or direction_selection == 'past' and line.date_maturity > date_from \
                or direction_selection == 'future' and line.date_maturity < date_from:
                if line.debit:
                    value = line.debit 
                else:
                    value = line.credit
                result_list[0] = value
                                    
           if line.date_maturity >= data['form']['4']['start'] and line.date_maturity <= data['form']['4']['stop']:
               if line.debit:
                   value = line.debit 
               else:
                   value = line.credit
               result_list[1] = value
                                    
           if line.date_maturity >= data['form']['3']['start'] and line.date_maturity <= data['form']['3']['stop']:
               if line.debit:
                   value = line.debit 
               else:
                   value = line.credit
               result_list[2] = value
            
           if line.date_maturity >= data['form']['2']['start'] and line.date_maturity <= data['form']['2']['stop']:
               if line.debit:
                   value = line.debit 
               else:
                   value = line.credit
               result_list[3] = value  
                                     
           if line.date_maturity >= data['form']['1']['start'] and line.date_maturity <= data['form']['1']['stop']:
               if line.debit:
                   value = line.debit 
               else:
                   value = line.credit
               result_list[4] = value                         
                            
           if line.date_maturity and data['form']['0']['stop'] and line.date_maturity <= data['form']['0']['stop'] or line.date_maturity and data['form']['0']['start'] and line.date_maturity >= data['form']['0']['start']:
               if line.debit:
                   value = line.debit 
               else:
                   value = line.credit
               result_list[5] = value
               
           #Total by partner        
           partner_total += line.debit if line.debit else line.credit * -1 
           result_list[6] = partner_total 
           
           res[line.id] = result_list
       
       return res, partner_total
        