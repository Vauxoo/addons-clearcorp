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

from osv import fields, orm
from collections import OrderedDict

class accountFinancialreport(orm.Model):
    
    _name =  "account.financial.report"
    _inherit =  "account.financial.report"
    
    '''
        This method obtain the structure for a account_financial_report (must be view type).
        Return a dictionary with a complete structure and the values. 
        The report's parses receive this structure and work with the data and return the 
        structure that must print the mako.
        
        @param acc_financial_id: Account financial report ID. Comes from the wizard of the report and must be view type.
        
    '''
    def get_structure_account_financial_report(self, cr, uid, acc_financial_id=None, context=None):

        account_obj = self.pool.get('account.account')
        account_type_obj = self.pool.get('account.account.type')
        library_obj = self.pool.get('account.webkit.report.library')
        
        #Use OrderedDict() to dictionary respect alphabetic order for account_type code
        #http://docs.python.org/2/library/collections.html#collections.OrderedDict        
        account_types_child = OrderedDict() 
        order_dict = OrderedDict()
        account_child = OrderedDict()        
        
        #Main dictionary structure.
        main_structure = {
            'name': '',                 #account.financial.report name
            'type':'',                  #type (sum, accounts, account_type, account_report)
            'display_type':'',          #display type (no_detail, detail_flat, detail_with_hierarch)
            'style': '',
            'child':[],                 #If the account_financial_report selected is parent of another records
            'account_type': [],          #If the account_financial_report selected is account_type type
            'account_type_child': {},    #Dictionary: (id of account_type is the key)  list of accounts that match with the account_type
            'accounts': [],              #List of accounts selected for account_financial_report
            'account_child': {}          #Dictionary: (id of account_type is the key)  list of accounts that match with the account
        }
                
        #1. Search the account_financial_report that match with acc_financial_id
        parent_acc_fin_report = self.browse(cr, uid, acc_financial_id, context=context)
        
        #2. Build the main dictionary 
        for parent in [parent_acc_fin_report]:
            main_structure['name'] = parent.name
            main_structure['code'] = parent.id
            main_structure['type'] = parent.type
            main_structure['display_detail'] = parent.display_detail
            main_structure['style'] = parent.style_overwrite
            
            '''TODO: Implement account_report (Valor en informe)'''            
            #3. Two cases: Type accounts or accounts. View is ignore.
            if parent.type == 'account_type':
                #Search the accounts that match with id type
                for type in parent.account_type_ids:
                    #Create order_dict to sort account_type by code.
                    order_dict[type.code] = type
                    main_structure['account_type'].append(type)
                
                #Search all the accounts that match with type selected. (Sort list by code)
                for key in order_dict.keys():
                    #With OrderedDict(), keep alphabetic order.
                    account_type = order_dict[key]
                    accounts_ids = account_obj.search(cr, uid, [('user_type','=',account_type.id)])
                    accounts = account_obj.browse(cr, uid, accounts_ids)                    
                    account_types_child[account_type] = accounts
            
                main_structure['account_type_child'] = account_types_child
                
            elif parent.type == 'accounts':                
                #Check if display_type is detail_with_hierarch, get the child's account
                for account in parent.account_ids:    
                    order_dict[account.code] = account
                    main_structure['accounts'].append(account)
                
                #Get all the child for account selected.                     
                #if parent.display_detail == 'detail_with_hierarchy':
                for key in order_dict.keys():
                    #With OrderedDict(), keep alphabetic order.
                    account =  order_dict[key]
                    child_ids = library_obj.get_account_child_ids(cr, uid, account.id,context)
                    child_obj = account_obj.browse(cr, uid, child_ids)
                    account_child[account] = child_obj
                main_structure['account_child'] = account_child
                
            ########################################################################################
            
            #4. Create a recursive method. Check if the account_financial_report have children.
            account_financial_child = self.search(cr, uid, [('parent_id.id','=', acc_financial_id)], order='sequence asc')
                            
            if len(account_financial_child) > 0:
                account_financial_child_obj = self.browse(cr, uid, account_financial_child)
                
                for child in account_financial_child_obj:
                    main_structure['child'].append(self.get_structure_account_financial_report(cr, uid, child.id))
        
        return main_structure 
    