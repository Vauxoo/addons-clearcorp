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

from osv import osv,fields, orm
from datetime import datetime
import time 
from openerp.tools.translate import _

class accountMoveinherit(orm.Model):
    
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']
    
    def create(self, cr, uid, vals, context={}):
        res = super(accountMoveinherit, self).create(cr, uid, vals, context)
        
        # Find users for Financial Manager Group and they will be add as
        # followers in the account.move thread
        
        #1. Find financial Manager group (find external id)
        res_id = self.pool.get('ir.model.data').search(cr, uid, [('name', '=', 'group_account_manager'),('module','=','account'),('model','=','res.groups')], limit=1)
        res_obj = self.pool.get('ir.model.data').browse(cr, uid, res_id, context=context)[0]
        
        #2. Find users
        user_ids = self.pool.get('res.users').search(cr, uid, [('groups_id','in', [res_obj.res_id])])
        
        #3.Call method message_subscribe_users (mail.thread) that receive account.move id and
        # user_ids (this method update followers list)
        
        #parameter res is the id that return super method.
        self.message_subscribe_users(cr, uid, [res], user_ids=user_ids, context=context)
        
        return res        
    
    def post(self, cr, uid, ids, context=[]):
       context = {}       
       account_ids = []
       
       account_obj = self.pool.get('account.account')
       fiscal_year_obj = self.pool.get('account.fiscalyear')
       
       #==== Do the super first for this method.        
       res = super(accountMoveinherit, self).post(cr, uid, ids, context=context)
       
       if res:           
           # Search account move lines for this account move.
           # Check their account and create a list of accounts with overdraft check activated.
           # Then, call compute of account and calculate their balance for entire fiscal year
           #----------------------------------------------------------------------------------- 
           # The alert is given if the amount is reversed depending on the configuration of the account.
           # If it is negative and the account is configured to debit launch a warning,
           # and if positive credit account is configured, launch an alert
           
           #Add parameters for compute method in account: fiscal_year and period list 
           #======== Actual fiscal year
           now = time.strftime('%Y-%m-%d')
           company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
           domain = [('company_id', '=', company_id), ('date_start', '<', now),('date_stop','>', now)]
           fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
           
           #======== Period list
           period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','in', fiscalyears)])
                  
           #=====update context
           context.update({'fiscalyear': fiscalyears[0], 'periods':period_ids})
          
           for moves in self.browse(cr, uid, ids, context=context):
               #=== 1. Extract account_id for those accounts with overdraft check activated. 
               for line in moves.line_id:
                   if (line.account_id.overdraft) and (line.debit > 0 or line.credit > 0):
                       account_ids.append(line.account_id.id)
               
               # If exists accounts with overdraft 
               if len(account_ids) > 0:
                   #==== 2. Call compute method.      
                   balance_account_today = account_obj._account_account__compute(cr, uid, account_ids, ['balance'], context=context)
                   
                   #==== 3. Check account's balance (iterate in account_ids list)
                   for account in account_obj.browse(cr, uid, account_ids, context=context):
                       balance = balance_account_today[account.id]['balance']
                       
                       #======= 4. If exists overdraft, create a message                   
                       if (balance > 0) and (account.standard_balance == 'credit'):
                           msg = _("The account move %s overdraft the account %s %s.") % \
                                (moves.name, account.code, account.name)
                           self.message_post(cr, uid, [moves.id], body=msg, context=context)
                        
                       if (balance < 0) and (account.standard_balance == 'debit'):
                           msg = _("The account move %s overdraft the account %s %s.") % \
                                (moves.name, account.code, account.name)
                           self.message_post(cr, uid, [moves.id], body=msg, context=context)
           
           return res        