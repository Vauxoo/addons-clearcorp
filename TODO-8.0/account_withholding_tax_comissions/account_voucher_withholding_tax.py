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

from openerp.osv import fields, osv, orm

class accountVoucherinherit(orm.Model):
    
    _name = "account.voucher"
    _inherit = "account.voucher"
    
    #Get move_lines for withholding tax
    def _get_withholding_move_lines(self, cr, uid, ids, *a):
        res = {}
        for voucher in self.browse(cr, uid, ids):
            move_ids = []
            for move in voucher.withholding_move_ids:
                move_ids.append(move.id)
                
            move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('move_id','in',move_ids)])
            res[voucher.id] = move_line_ids
            
        return res       
    
    #Get move_lines reverse for withholding tax reverse
    def _get_withholding_move_lines_reverse(self, cr, uid, ids, *a):
        res = {}
        for voucher in self.browse(cr, uid, ids):
            move_ids = []
            for move in voucher.withholding_move_ids:
                if move.move_reverse_id:
                    move_ids.append(move.move_reverse_id.id)
                
            move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('move_id','in',move_ids)])
            res[voucher.id] = move_line_ids
            
        return res  

    #Create a method that set the withholding tax from journal to voucher.
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):     
         
        vals = super(accountVoucherinherit, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        
        required_list = []
        optional_list = []
            
        if journal_id:
            #Get complete object to extract withholding tax.
            journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_id, context)
            
            #Get ids for m2m fields
            for required in journal_obj.withholding_tax_required:
                required_list.append(required.id)
            
            for optional in journal_obj.withholding_tax_optional:
                optional_list.append(optional.id)
            
            #Pass values to account.voucher            
            #Put the same values in voucher_withholding_tax_required_vis and voucher_withholding_tax_required_inv
            #Because when the journal change, both change too and they have the same value at the same time. 
            vals['value'].update({'withholding_tax_required_view': required_list})
            vals['value'].update({'withholding_tax_required': required_list})
            vals['value'].update({'withholding_tax_optional': optional_list})
        
        else:
            #Remove the previous values in case that don't exist journal selected
            vals = {'value':{} }
            vals['value'].update({'withholding_tax_required_view': required_list})
            vals['value'].update({'withholding_tax_required': required_list})
            vals['value'].update({'withholding_tax_optional': optional_list})

        return vals
    
        """
              IMPORTANT: Withholding tax required are readonly. Because it is readonly, the field doesn't save normally, in the moment of push
              button save. So, create a workarrond with two fields with the same relation in database (same name, in this case, voucher_withholding_tax_required), and
              two fields are the same.
              
              In the xml, voucher_withholding_tax_required_vis has attribute readonly and voucher_withholding_tax_required_inv has the attribute invisible, the user
              sees the field voucher_withholding_tax_required_vis and in the moment to save the record, both point to same relation (voucher_withholding_tax_required)
              and the user sees that he put in the field, is readonly and the field store in database.
                
        """ 
    
    _columns = {
          'withholding_tax_optional': fields.many2many('account.withholding.tax', 'voucher_withholding_tax_optional', string="Optional Withholding Tax"),
          
          #Both fields have the same relation name in database (voucher_withholding_tax_required) that's the magic of the trick 
          #One field that user sees and other with the same value that store the value in database. 
          'withholding_tax_required_view': fields.many2many('account.withholding.tax', 'voucher_withholding_tax_required', string="Required Withholding Tax"),
          'withholding_tax_required': fields.many2many('account.withholding.tax', 'voucher_withholding_tax_required', string="Required Withholding Tax"),     
          
          'withholding_move_ids':fields.one2many('account.move', 'withholding_voucher_id', 'Withholding Move'),
          'withholding_move_line_ids':fields.function(_get_withholding_move_lines, string='Account Move Lines Withholding Tax', type='one2many', relation='account.move.line'),
          'withholding_move_line_ids_reverse':fields.function(_get_withholding_move_lines_reverse, string='Account Move Lines Reverse Withholding Tax', type='one2many', relation='account.move.line'),
     }    
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'withholding_move_ids': False,
        })
        return super(accountVoucherinherit, self).copy(cr, uid, id, default, context=context)
    
    #Check if the required withholding tax are in optional withholding tax
    def _check_duplicate_withholding_tax(self, cr, uid, ids, context=None):
         
         withholding_voucher_obj = self.browse(cr, uid, ids[0],context)
                  
         list_required =  []
         list_optional =  []
    
         for required in withholding_voucher_obj.withholding_tax_required:
             list_required.append(required.id)
        
         for optional in withholding_voucher_obj.withholding_tax_optional:
             list_optional.append(optional.id)
    
         for element in list_required:
             if element in list_optional:
                 return False
        
         return True
     
    _constraints = [
        (_check_duplicate_withholding_tax,'Withholding tax can not be the same for required and optional !',['voucher_withholding_tax_optional']),
    ]   
    
    #Method that create the move and move lines from withholding tax
    def action_move_line_create(self, cr, uid, ids, context=None):
                
        #1. Super of action_move_line_create
        res = super(accountVoucherinherit, self).action_move_line_create(cr, uid, ids, context)        

        for voucher in self.browse(cr, uid, ids, context=context):           
            # Currency of voucher and company
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
                
            # For each withholding tax, keep amount or percentage.            
           
            #*****************REQUIRED WITHHOLDING TAX
            # For required withholding tax, use voucher_withholding_tax_required_inv field
            for withholding in voucher.withholding_tax_required:                   
                
                #********************MOVE
                #Create move_id (the method account_move_get return a dictionary)
                
                move_id_name = voucher.move_id.ref + ' ' + withholding.code 
                move_dict = self.account_move_get(cr, uid, voucher.id, context=context)
                
                move_dict['name'] = '/'
                move_dict['journal_id'] = withholding.journal_id.id
                move_dict['ref'] = move_id_name
                move_dict['narration'] = move_id_name           
                
                #Associate voucher with move
                move_dict['withholding_voucher_id'] =  voucher.id         
                
                move_id = self.pool.get('account.move').create(cr, uid, move_dict, context=context)  
                   
                ##*******************AMOUNTS
                if company_currency <> current_currency:
                    if withholding.type == 'percentage':
                        withholding_amount = voucher.amount * (withholding.amount / 100)
                        amount_currency = withholding_amount
                    else:
                        withholding_amount = withholding.amount
                        amount_currency = (withholding.amount * voucher.paid_amount_in_company_currency) / voucher.amount                    
                else:
                    #For each withholding tax, create two move lines
                    #Get amount or percentage associate to withholding tax
                    if withholding.type == 'percentage':
                        withholding_amount = voucher.paid_amount_in_company_currency * (withholding.amount / 100)
                    else:
                        withholding_amount = withholding.amount
                    
                    amount_currency = 0.0                        
                #**************************
                
                #********************ACCOUNTS
                #Get account to associate the move line and debit or credit
                if voucher.type in ('purchase', 'payment'):
                    account_debit = voucher.account_id
                    account_credit = withholding.journal_id.default_credit_account_id
                
                elif voucher.type in ('sale', 'receipt'):
                    account_debit = withholding.journal_id.default_debit_account_id
                    account_credit = voucher.account_id            
                #****************************
                
                #Line name
                line_name = voucher.move_id.ref + ' ' + withholding.code                
                        
                #create move_lines (2 for each withhlding):
                move_line_debit = {
                    'name': line_name,
                    'debit': withholding_amount,
                    'credit': 0.0,
                    'account_id': account_debit.id,
                    'move_id': move_id,
                    'journal_id': withholding.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': amount_currency,
                    'date': voucher.date,
                    'date_maturity': voucher.date_due
                }
                
                move_line_credit = {
                    'name': line_name,
                    'debit': 0.0,
                    'credit': withholding_amount,
                    'account_id': account_credit.id,
                    'move_id': move_id,
                    'journal_id': withholding.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': amount_currency,
                    'currency_id': 0.0,
                    'amount_currency':0.0,
                    'date': voucher.date,
                    'date_maturity': voucher.date_due
                }
                
                #Create move_lines
                self.pool.get('account.move.line').create(cr, uid, move_line_credit, context)
                
                self.pool.get('account.move.line').create(cr, uid, move_line_debit, context)               
                
                
            #*****************OPTIONAL WITHHOLDING TAX
            # For required withholding tax, use voucher_withholding_tax_required_inv field
            for withholding in voucher.withholding_tax_optional:                
                
                #********************MOVE
                #Create move_id (the method account_move_get return a dictionary)
                
                move_id_name = voucher.move_id.ref + ' ' + withholding.code 
                move_dict = self.account_move_get(cr, uid, voucher.id, context=context)
                
                move_dict['name'] = '/'
                move_dict['journal_id'] = withholding.journal_id.id
                move_dict['ref'] = move_id_name
                move_dict['narration'] = move_id_name           
                
                #Associate voucher with move
                move_dict['withholding_voucher_id'] =  voucher.id         
                
                move_id = self.pool.get('account.move').create(cr, uid, move_dict, context=context)  
                   
                ##*******************AMOUNTS
                #Check if voucher currency is diferent that currency company
                if company_currency <> current_currency:
                    if withholding.type == 'percentage':
                        withholding_amount = voucher.amount * (withholding.amount / 100)
                        amount_currency = withholding_amount
                    else:
                        withholding_amount = withholding.amount
                        amount_currency = (withholding.amount * voucher.paid_amount_in_company_currency) / voucher.amount
                    
                else:
                    if withholding.type == 'percentage':                       
                       withholding_amount = voucher.paid_amount_in_company_currency * (withholding.amount / 100)
                       
                    else:
                        withholding_amount = withholding.amount
                    
                    amount_currency = 0.0
                        
                #**************************
                
                #********************ACCOUNTS
                #Get account to associate the move line and debit or credit
                if voucher.type in ('purchase', 'payment'):
                    account_debit = voucher.account_id
                    account_credit = withholding.journal_id.default_credit_account_id
                
                elif voucher.type in ('sale', 'receipt'):
                    account_debit = withholding.journal_id.default_debit_account_id
                    account_credit = voucher.account_id
            
                #****************************
                
                #Line name
                line_name = voucher.move_id.ref + ' ' + withholding.code                
                        
                #create move_lines (2 for each withhlding):
                move_line_debit = {
                    'name': line_name,
                    'debit': withholding_amount,
                    'credit': 0.0,
                    'account_id': account_debit.id,
                    'move_id': move_id,
                    'journal_id': withholding.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': amount_currency,
                    'date': voucher.date,
                    'date_maturity': voucher.date_due
                }
                
                move_line_credit = {
                    'name': line_name,
                    'debit': 0.0,
                    'credit': withholding_amount,
                    'account_id': account_credit.id,
                    'move_id': move_id,
                    'journal_id': withholding.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': amount_currency,
                    'currency_id': 0.0,
                    'amount_currency':0.0,
                    'date': voucher.date,
                    'date_maturity': voucher.date_due
                }
                
                #Create move_lines
                self.pool.get('account.move.line').create(cr, uid, move_line_credit, context)
                
                self.pool.get('account.move.line').create(cr, uid, move_line_debit, context)

        return True

    #When the voucher reverse, the account move for withholding tax reverse too.
    def reverse_voucher(self, cr, uid, ids, context=None):
        
        reverse_withholing_list = []
        
        #Reverse "normal" voucher.
        res = super(accountVoucherinherit, self).reverse_voucher(cr, uid, ids, context)   
        
        #Reverse "withholding voucher"
        for voucher in self.browse(cr, uid, ids, context=context):
            for withholding_move in voucher.withholding_move_ids:
                self.pool.get('account.move').reverse(cr, uid, [withholding_move.id], context=context)
            self.write(cr, uid, [voucher.id], {'state' : 'reverse'}, context=context)
                        
        return res