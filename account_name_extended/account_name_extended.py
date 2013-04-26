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

import re
from osv import osv, fields
from openerp.tools import translate

class account_account(osv.osv):
    _name = "account.account"
    _inherit = "account.account"
    
    #Change the way that the user can see the account when is search in a many2one field.
    #Add the company prefix in the name of the company and the shortcurt of the parent's account.
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for obj_account in self.browse(cr,uid,ids):
            obj_company = self.pool.get('res.company').browse(cr,uid,obj_account.company_id.id)
            #If the company of the account have prefix, add in the account's name. 
            prefix= obj_company.prefix
            if prefix == False:
                prefix = ''
            data = []
            account = obj_account.parent_id
            #Add the parent's name shortcut.
            if account.parent_id:
                while account.parent_id:
                    data.insert(0,(account.shortcut or account.name))
                    account = account.parent_id
                data.append(obj_account.name)
                data = '/'.join(data)
                data = obj_account.code + ' ' + data
                data = prefix and prefix + '-' + data or data
            else:
                #If there not exist a parent, concat the account's name. 
                data.append(obj_account.name)
                data = '/'.join(data)
                data = prefix and prefix + ' ' + data or data
            res.append((obj_account.id, data))
        return res
    
    
    #Add the company prefix and the regular expression that permit search include the special characteres.    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        ids =  list = account_ids = ids_company = []
        code = code_regular = new_code = ''        
        regular_expresion = '%'
        
        if not args:
            args = []       
            
        if name:           
            company_ids = self.pool.get('res.company').search(cr, uid, [])
            code = name 
            code = code.replace('-','').replace('_', '').replace('.','').replace(' ','')
           
            for c in code:
                new_code += c + regular_expresion            
                
            ids += self.search(cr, uid, [('code', 'ilike', new_code)], limit=limit)
        
            ids+= self.search(cr, uid, [('shortcut', '=', name)], limit=limit)
       
            ids+= self.search(cr, uid, [('name', operator, name)], limit=limit)
                                       
            for company in self.pool.get('res.company').browse(cr, uid, company_ids):
                prefix = company.prefix
                if prefix != False:
                    if name.lower().find(prefix) == 0:
                        len_sub = len(company.prefix) #Find the size of the prefix
                        code = name[len_sub:]   #Create a substring without the prefix
                        new_name = name[len_sub:] #Save the original name without the prefix to search the name and the shortcut
                        
                        code.replace('-','').replace('_', '').replace('.','').replace(' ','')
                        
                        for c in code:
                            code_regular += c + regular_expresion
                        
                        list += ['&',('company_id','=', company.name), ('code', '=like', code_regular)]                            
                        list += ['&',('company_id','=', company.name), ('shortcut', '=', new_name)]
                        list += ['&',('company_id','=', company.name), ('name', operator, new_name)]
                        
                        ids_company = self.search(cr, uid, list, limit=limit)
                        ids += ids_company

            #If any account are repeat
            for account in ids:
                if account not in account_ids:
                    account_ids.append(account)
                         
        return self.name_get(cr, uid, account_ids, context=context) #search the names that match with the ids.

class account_journal(osv.osv):
    _name = "account.journal"
    _inherit = "account.journal"    
    
    #Add the company prefix to the journal name.
    def name_get(self, cr, user, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = self.browse(cr, user, ids, context=context)
        res = []
        for rs in result:
            obj_company = self.pool.get('res.company').browse(cr,user,rs.company_id.id)
            prefix= obj_company.prefix
            if prefix == False:
                prefix = ''
            data = []
            data.append(rs.name)
            data = '-'.join(data)
            data = prefix and prefix + ' ' + data or data
            res.append((rs.id, data))
            
        return res
    
    #Add company prefix to the journal search. 
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        
        if not args:
            args = []
        if context is None:
            context = {}
        
        ids = journal_ids = list = []
        
        if context.get('journal_type', False):
            args += [('type','=',context.get('journal_type'))]
        if name:
            ids = self.search(cr, user, [('code', 'ilike', name)]+ args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', 'ilike', name)]+ args, limit=limit, context=context)#fix it ilike should be replace with operator

        company_ids = self.pool.get('res.company').search(cr, user, [])
        for company in self.pool.get('res.company').browse(cr, user, company_ids):
            prefix = company.prefix
            if prefix != False:
                if name.lower().find(prefix) == 0:
                    len_sub = len(company.prefix) #Find the size of the prefix
                    new_name = name[len_sub:] #Extract the name without the prefix

                    list += ['&',('company_id','=', company.name), ('code', '=like', new_name)]
                    list += ['&',('company_id','=', company.name), ('name', operator, new_name)]
                    
            ids += self.search(cr, user, list + args, limit=limit)
            #If any journal are repeat
            for journal in ids:
                if journal not in journal_ids:
                    journal_ids.append(journal)
                         
        return self.name_get(cr, user, journal_ids, context=context) #search the names that match with the ids.
                   
                        
class account_fiscalyear(osv.osv):
    '''
    Adds up to 16 chars to a Fiscal year code
    '''
    _name = 'account.fiscalyear'
    _inherit = 'account.fiscalyear'
    
    _columns = {
        'code': fields.char('Code', size=16, required=True, help="The code will be used to generate the numbers of the journal entries of this journal."),
    }

class account_period(osv.osv):
    '''
    Adds up to 16 chars to a Fiscal year code
    '''
    _name = 'account.period'
    _inherit = 'account.period'
    
    _columns = {
        'code': fields.char('Code', size=16),
    }
