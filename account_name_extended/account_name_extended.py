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
from openerp.osv import osv, fields
from openerp.tools import translate

class account_account(osv.Model):
    _name = "account.account"
    _inherit = "account.account"

    #Change the way that the user can see the account when is search in a many2one field.
    #Add the company prefix in the name of the company and the shortcurt of the parent's account.
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        
        #Avoid problem when only an account is selected
        if isinstance(ids, int):
            accounts = [self.browse(cr,uid,ids)]
        else:
            accounts = self.browse(cr,uid,ids)
        
        for obj_account in accounts:
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
                #If there not exist a parent, concatenated the account's name. 
                data.append(obj_account.name)
                data = '/'.join(data)
                data = prefix and prefix + ' ' + data or data
            res.append((obj_account.id, data))
        return res
    
    #Add the company prefix and the regular expression that permit search include the special characters.
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        account_ids = company_ids = search_domains = []
        dict_prefix = {}
        regular_expresion_number = '^[0-9.-_]+$'

        if not args:
            args = []
        
        #Code doesn't start with first word by numbers or special characters
        #Name doesn't start with numbers. 
        if name:
            piece_1 = piece_2 = piece_3 = ''
            #Method partition return a tuple that contains the first part before the separator (in this case ' ') and the other position
            #is the rest of the sentence.
            temp_partition = name.partition(' ')
            piece_1 = temp_partition[0]
            piece_2 = temp_partition[2]
            
            company_ids = self.pool.get('res.company').search(cr, uid, [])
            companies = self.pool.get('res.company').browse(cr, uid, company_ids)
            
            for company in companies:
                if company.prefix:
                    dict_prefix[company.id] = company.prefix

            #1.If prefixes and Company.
            # dict_prefix has the id of the company with its own prefix
            if dict_prefix:
                for id, prefix in dict_prefix.iteritems():
                    if piece_1.lower() in prefix.lower():
                        company_ids.append(id)
                    if company_ids: #Companies that match the prefix
                        #If the prefix is a number
                        if re.match(regular_expresion_number, piece_1):
                            if piece_2: #If something is typed after the prefix.
                                piece_2_b = piece_2.partition(' ')[0]
                                #if a number is first
                                if re.match(regular_expresion_number, piece_2_b):
                                    search_domains.append({
                                                          'company_ids':company_ids, 
                                                          'code':piece_2_b,
                                                          'name':piece_2.partition(' ')[2]
                                                          }) 
                                else:
                                    #If anything.
                                    search_domains.append({
                                                          'company_ids':company_ids, 
                                                          'name':piece_2
                                                          })
                                search_domains.append({'code': piece_1,
                                                       'name':piece_2})
                                
                            else:
                                #If this is not addressed then the prefix digit
                                search_domains.append({'company_ids':company_ids})
                                search_domains.append({'code':piece_1})
                        else:
                            #if the prefix is not a number
                            #If something is typed after the prefix
                            if piece_2:
                                piece_2_b = piece_2.partition(' ')[0]
                                piece_3 = piece_2.partition(' ')[2]
                                #If it is a number
                                if re.match(regular_expresion_number, piece_2_b):
                                    search_domains.append({
                                                          'company_ids':company_ids, 
                                                          'code':piece_2_b,
                                                          'name':piece_3
                                                          })
                                else:
                                    #If it is not a number
                                    search_domains.append({
                                                          'company_ids':company_ids, 
                                                          'name':piece_2})
                                
                                search_domains.append({'name':name})
                            
                            else:
                                #If not then you type the prefix
                                search_domains.append({'company_ids':company_ids})
                                search_domains.append({'name':name})
                    else:
                        #If the prefix is not a number
                        if re.match(regular_expresion_number, piece_1):
                            search_domains.append({
                                                   'code':piece_1,
                                                   'name':piece_2
                                                  })
                        else:
                            search_domains.append({'name':name})
            #If there is no prefix.
            else:
                if re.match(regular_expresion_number, piece_1):
                    search_domains.append({
                                           'code':piece_1,
                                           'name':piece_2
                                          })
                else:
                    search_domains.append({'name':name})
            
            #Build the search domain for the account browser.
            search_domain = []
            regular_expresion = '%'
            for domain in search_domains:
                temp_domain = []
                if 'company_ids' in domain.keys():
                    temp_domain.append(('company_id','in', domain['company_ids']))
                
                if 'code' in domain.keys():
                     code = domain['code']
                     code = code.replace('-','').replace('_', '').replace('.','')
                     new_code = regular_expresion 
            
                     for c in code:
                         new_code += c + regular_expresion
                         
                     temp_domain.append(('code', '=like', new_code))
                
                if 'name' in domain.keys():
                    if domain['name']:
                        temp_domain.append(('name', operator, domain['name']))
            
                #Depend of the quantity of domain, add the & or the '|'.
                if len(temp_domain) == 1:
                    search_domain += temp_domain
                    
                elif len(temp_domain) == 2:
                    search_domain.append('&')
                    search_domain += temp_domain
                
                else:
                    search_domain.append('&')
                    search_domain.append('&')
                    search_domain += temp_domain
            
            number_or = (len(search_domains) / 2) - 1
            cont = 0
            while cont < number_or:
                search_domain = ['|'] + search_domain
                cont += 1
            
            account_ids = self.pool.get('account.account').search(cr, uid, search_domain + args, limit=limit, context=context)
        
        else:
            account_ids = self.pool.get('account.account').search(cr, uid, [] +args, limit=limit, context=context)
        
        return self.name_get(cr, uid, account_ids, context=context) #search the names that match with the ids.

class account_journal(osv.Model):
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
            data.append(rs.code)
            data.append(rs.name)
            data = ' - '.join(data)
            data = prefix and prefix + ' ' + data or data
            res.append((rs.id, data))
        
        return res

    #Add company prefix to the journal search. 
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        #TODO: Pass comments to english
        journal_ids = company_ids = search_domains = []
        dict_prefix = {}
        
        if not args:
            args = []
        
        if name:
            piece_1 = piece_2 = ''
            #Method partition return a tuple that contains the first part before the separator (in this case ' ') and the other position
            #is the rest of the sentence.
            temp_partition = name.partition(' ')
            piece_1 = temp_partition[0]
            piece_2 = temp_partition[2]
            
            company_ids = self.pool.get('res.company').search(cr, uid, [])
            companies = self.pool.get('res.company').browse(cr, uid, company_ids)
            
            for company in companies:
                if company.prefix:
                    dict_prefix[company.id] = company.prefix

            #1. if have prefix and company
            # dict_prefix has the id of the company with your prefix respective
            for id, prefix in dict_prefix.iteritems():
                    if piece_1.lower() in prefix.lower():
                        company_ids.append(id)

            # Both conditions must be met to have prefix.
            if dict_prefix and company_ids:
                #P2 if there (followed by "typing" after the prefix)               
                if piece_2:
                    piece_2_b = piece_2.partition(' ')[0] 
                    piece_3 = piece_2.partition(' ')[2]
                    
                    #Domains
                    search_domains.append({
                                            'code':piece_2_b,
                                            'name':piece_3,
                                            'company_ids':company_ids
                                           })
                    
                    search_domains.append({'company_ids':company_ids,
                                           'name':piece_2})
                    
                    search_domains.append({'name': name })
                    search_domains.append({
                                           'code':piece_1,
                                           'name':name,
                                          })
                                   
                else:
                    search_domains.append({
                                           'company_ids':company_ids,
                                           'name':piece_1,
                                           'code':piece_1})
            
            #If no prefix ...
            else:
                if piece_2: #If continued typing
                    search_domains.append({'name': name })
                    search_domains.append({
                                           'code':piece_1,
                                           'name':piece_2,
                                           })
                #If only one word is typed at the beginning of the search.
                else:
                    search_domains.append({
                                           'code':piece_1,
                                           'name':piece_1,
                                          })
            
            #Build the search domain for the account browser.
            search_domain = []
            regular_expresion = '%'
            for domain in search_domains:
                temp_domain = []
                if 'company_ids' in domain.keys():
                    temp_domain.append(('company_id','in', domain['company_ids']))
                
                if 'code' in domain.keys():
                     code = domain['code']
                     code = code.replace('-','').replace('_', '').replace('.','')
                     new_code = regular_expresion 
                 
                     for c in code:
                         new_code += c + regular_expresion
                         
                     #ilike is case sensitive
                     temp_domain.append(('code', 'ilike', new_code))
                
                if 'name' in domain.keys():
                    if domain['name']:
                        temp_domain.append(('name', operator, domain['name']))
                
                #Depend of the quantity of domain, add the & or the '|'    
                #Unlike account can match any change so the '&' by '|'
                if len(temp_domain) == 1:
                    search_domain += temp_domain
                    
                elif len(temp_domain) == 2:
                    search_domain.append('|')
                    search_domain += temp_domain
                
                else:
                    search_domain.append('|')
                    search_domain.append('&')
                    search_domain += temp_domain
            
            number_or = (len(search_domains) / 2) - 1
            cont = 0
            while cont < number_or:
                search_domain = ['|'] + search_domain
                cont += 1
                    
            journal_ids = self.pool.get('account.journal').search(cr, uid, search_domain + args, limit=limit, context=context)
            
        else:
            journal_ids = self.pool.get('account.journal').search(cr, uid, [] + args, limit=limit, context=context)
    
        return self.name_get(cr, uid, journal_ids, context=context) #search the names that match with the ids.

class account_fiscalyear(osv.Model):
    '''
    Adds up to 16 chars to a Fiscal year code
    '''
    _name = 'account.fiscalyear'
    _inherit = 'account.fiscalyear'
    
    _columns = {
        'code': fields.char('Code', size=16, required=True, help="The code will be used to generate the numbers of the journal entries of this journal."),
    }

class account_period(osv.Model):
    '''
    Adds up to 16 chars to a Fiscal year code
    '''
    _name = 'account.period'
    _inherit = 'account.period'
    
    _columns = {
        'code': fields.char('Code', size=16),
    }