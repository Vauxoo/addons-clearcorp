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

import copy
from osv import osv, fields
from tools.translate import _

class AccountAccount(osv.osv):
    _inherit = "account.account"
    
    _columns = {
        'exchange_rate_adjustment': fields.boolean('Exchange rate adjustment', help="Choose if the account needed an adjusted exchange rate"),
        'rate_adjustment': fields.selection([('primary','Primary'),('secondary','Secondary')], "Rate Adjustment"),
    }

    def onchange_currency(self, cr, uid, ids, currency_id, context=None):
        res = {}
        
        #if currency has not second_rate, establish primary as default option
        if currency_id:
            currency_obj = self.pool.get('res.currency').browse(cr, uid, currency_id,context=context)
            if not currency_obj.second_rate:
                res = {'value': {'rate_adjustment': 'primary'} }
            else:
                res = {'value': {'rate_adjustment': ''} }
        
        return res
    
    """
        Redefine create and write. It exists a "bug", when field selection rate_adjustment
        is readonly, the value doesn't save when the account is created or written. 
        Check if currency has not second_rate and rate_adjustment is secondary, throw an
        exception. 
    """
    
    def create(self, cr, uid, vals, context={}):
        if 'currency_id' in vals.keys() and vals['currency_id']:
            if 'rate_adjustment' in vals.keys():
                currency = self.pool.get('res.currency').browse(cr, uid, vals['currency_id'], context=context)
                if not currency.base and not currency.second_rate and (vals['rate_adjustment'] == 'secondary'):
                    raise osv.except_osv(_('Error!'), _('The secondary currency does not allow secondary rate adjustment\n'))
                    
        return super(AccountAccount, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        #if currency_id doesn't allow second_rate, rate_adjustment must be primary
        for account in self.browse(cr, uid, ids, context=context):
            if account.currency_id:
                if 'rate_adjustment' in vals.keys():
                    if not account.currency_id.base and not account.currency_id.second_rate and (vals['rate_adjustment'] == 'secondary'):
                        raise osv.except_osv(_('Error!'), _('The secondary currency does not allow secondary rate adjustment\n'))
                        
        return super(AccountAccount, self).write(cr, uid, ids, vals, context=context)
    
class AccountMoveLine(osv.osv):
    _name = "account.move.line"
    _inherit = "account.move.line"
    
    def _amount_exchange_rate(self, cr, uid, ids, field_names, args, context=None):
        """
           This function returns an amount of exchange rate base in the debit/credit and amount_currency,
           and returns an amount of exchange rate of the day.
        """
        res = {}
        if context is None:
            context = {}
        res_currency_obj = self.pool.get('res.currency')
        res_currency_rate_obj = self.pool.get('res.currency.rate')
        res_users_obj = self.pool.get('res.users')
        
        res_user = res_users_obj.browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id
        
        lines = self.browse(cr, uid, ids, context=context)
        for move_line in lines:
            res[move_line.id] = {
                'amount_exchange_rate': 0.0,
                'amount_base_import_exchange_rate': 0.0,
            }

            if not move_line.currency_id or move_line.amount_currency == 0:
                continue
            if move_line.debit and move_line.debit > 0.00:
                sign = move_line.amount_currency < 0 and -1 or 1
                result = sign * move_line.debit / move_line.amount_currency
                res[move_line.id]['amount_exchange_rate'] = res_currency_obj.round(cr, uid, move_line.currency_id, result) or result
            elif move_line.credit and move_line.credit > 0.00:
                sign = move_line.amount_currency < 0 and -1 or 1
                result = sign * move_line.credit / move_line.amount_currency
                res[move_line.id]['amount_exchange_rate'] = res_currency_obj.round(cr, uid, move_line.currency_id, result) or result
            res[move_line.id]['amount_base_import_exchange_rate'] = res_currency_obj.get_exchange_rate(cr, uid, move_line.currency_id, company_currency, move_line.date, context)
        return res
    
    _columns = {
        'amount_exchange_rate': fields.function(_amount_exchange_rate, string='Amount of exchange rate', multi="residual", help="The amount of exchange rate."),
        'amount_base_import_exchange_rate': fields.function(_amount_exchange_rate, string='Base amount exchange rate', multi="residual", help="Exchange rate in the system."),
        'adjustment': fields.many2one('account.move.line', 'Adjustment'),
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'adjustment':False,
        })

class AccountMove(osv.osv):
    _name = "account.move"
    _inherit = "account.move"
    
    def get_balance_amount(self, cr, uid, move_id, context):
        cr.execute( 'SELECT SUM(debit-credit) '\
                    'FROM account_move_line '\
                    'WHERE move_id = %s ', (move_id,))
        result = cr.fetchall()
        return result[0][0] or 0.00
    
    def get_adjustment_amount(self, cr, uid, move_id, context):
        cr.execute( 'SELECT SUM(debit-credit) '\
                    'FROM account_move_line '\
                    'WHERE adjustment = %s ', (move_id,))
        result = cr.fetchall()
        return result[0][0] or 0.00
        
    def create_move_lines_reconcile(self, cr, uid, move, exchange_rate_date, context=None):
        move_line_obj = self.pool.get('account.move.line')
        account_account_obj = self.pool.get('account.account')
        account_period_obj = self.pool.get('account.period')
        res_currency_obj = self.pool.get('res.currency')
        res_user_obj = self.pool.get('res.users')
        lines_created_ids = []
        
        account_reconcile_ids = account_account_obj.search(cr, uid, [('exchange_rate_adjustment', '=', True), ('reconcile', '=', True)], context=context)
        periods_ids = account_period_obj.get_interval_period(cr, uid, start_period=None, end_period=move.period_id, fiscal_year=move.period_id.fiscalyear_id.id, initial_balance=False)
        line_reconcile_ids = move_line_obj.search(cr, uid, [('date','<=',exchange_rate_date),('currency_id','!=',None), ('period_id','in',periods_ids), ('amount_currency','!=',0), ('account_id','in',account_reconcile_ids), ('adjustment','=',None), ('reconcile_id','=',None)], context=context)
        lines_reconcile = move_line_obj.browse(cr, uid, line_reconcile_ids, context=context)
        
        #Get current company for logged user.
        res_user = res_user_obj.browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id 
        
        for line in lines_reconcile:
            if not line.amount_currency:
                continue
            sign_amount_currency = line.amount_currency < 0 and -1 or 1
            line_difference = 0
            adjustment_amount = self.get_adjustment_amount(cr, uid, line.id, context=context)
            
            #Check if account in line use primary or second rate. 
            if line.account_id.exchange_rate_adjustment:
                if line.account_id.rate_adjustment == 'secondary':
                    second_rate = True
                else:
                    second_rate = False
            
            #Get exchange_amount, depends of account
            #primary -> sale
            #secondary -> purchase
            copy_context = copy.copy(context)
            copy_context.update({'second_rate':second_rate})
            copy_context.update({'date':exchange_rate_date})
            exchange_amount = res_currency_obj._current_rate(cr, uid, [company_currency.id], exchange_rate_date, arg=None, context=copy_context)[company_currency.id]
            
            if line.credit != 0.00:
                line_difference = sign_amount_currency * line.amount_currency * exchange_amount - line.credit
            elif line.debit != 0.00:
                line_difference = sign_amount_currency * line.amount_currency * exchange_amount - line.debit
            
            if line_difference == 0.00 and adjustment_amount == 0.00:
                continue
            
            #Calculation of line_difference_adjustment
            sign = line_difference < 0.00 and -1 or 1
            line_difference_adjustment = 0.00
            if line.credit != 0 and exchange_amount > line.amount_exchange_rate or line.debit != 0 and exchange_amount < line.amount_exchange_rate:
                line_difference_adjustment = sign * line_difference + adjustment_amount                
            elif line.credit != 0 and exchange_amount < line.amount_exchange_rate or line.debit != 0 and exchange_amount > line.amount_exchange_rate:
                line_difference_adjustment = sign * line_difference - adjustment_amount
            else:
                line_difference_adjustment = adjustment_amount
                
            #Calculation of credit and debit
            credit = 0.00
            debit = 0.00
            
            if line.credit != 0 and exchange_amount > line.amount_exchange_rate:
                credit = abs(line_difference_adjustment)
            elif line.credit != 0 and exchange_amount < line.amount_exchange_rate:
                if line_difference_adjustment < 0.00:
                    credit = abs(line_difference_adjustment)
                else:
                    debit = line_difference_adjustment
            elif line.debit != 0 and exchange_amount > line.amount_exchange_rate:
                if line_difference_adjustment < 0.00:
                    credit = abs(line_difference_adjustment)
                else:
                    debit = line_difference_adjustment
            elif line.debit != 0 and exchange_amount < line.amount_exchange_rate:
                if line_difference_adjustment < 0.00:
                    debit = abs(line_difference_adjustment)
                else:
                    credit = line_difference_adjustment
            elif exchange_amount == line.amount_exchange_rate:
                if line_difference_adjustment < 0.00:
                    debit = abs(line_difference_adjustment)
                else:
                    credit = line_difference_adjustment
            
            #Create move line
            move_line = {
                         'name': 'Adj ' + line.name or 'Adj',
                         'ref': line.ref or '',
                         'debit': debit,
                         'credit': credit,
                         'account_id':line.account_id.id,
                         'move_id': move.id,
                         'period_id': move.period_id.id,
                         'journal_id': line.journal_id.id,
                         'partner_id': line.partner_id.id,
                         'currency_id': line.account_id.currency_id.id,
                         'amount_currency': 0.00,
                         'state': 'valid',
                         'company_id': line.company_id.id,
                         'adjustment': line.id,
                         }
            new_move_line_id = move_line_obj.create(cr, uid, move_line, context=context)            
            move_line_obj.reconcile_partial(cr, uid, [line.id, new_move_line_id], 'auto', context)            
            lines_created_ids.append(new_move_line_id)
            
        return lines_created_ids
        
    def create_move_lines_unreconcile(self, cr, uid, move, period, exchange_rate_date, context=None):
        res_currency_obj = self.pool.get('res.currency')
        move_line_obj = self.pool.get('account.move.line')
        account_account_obj = self.pool.get('account.account')
        account_period_obj = self.pool.get('account.period')
        res_user_obj = self.pool.get('res.users')
        library_obj = self.pool.get('account.webkit.report.library')
        
        lines_created_ids = []
        
        #Get current company for logged user.
        res_user = res_user_obj.browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id      
        
        account_unreconcile_ids = account_account_obj.search(cr, uid, [('exchange_rate_adjustment', '=', True), ('reconcile', '=', False), ('currency_id', '!=', None)], context=context)
        period_ids = account_period_obj.get_interval_period(cr, uid, start_period=None, end_period=period, fiscal_year=period.fiscalyear_id.id, initial_balance=False)
        
        for account_id in account_unreconcile_ids:
            res = library_obj.get_account_balance(cr, uid, [account_id], ['balance', 'foreign_balance'],
                                                              fiscal_year_id = period.fiscalyear_id.id,
                                                              state='posted',
                                                              start_date = period.fiscalyear_id.date_start,
                                                              end_date = exchange_rate_date,
                                                              period_ids = period_ids)
            foreign_balance = res[account_id]['foreign_balance']
            balance = res[account_id]['balance']
            
            #Search account
            account = account_account_obj.browse(cr, uid, account_id, context=context)            
            #Check if account in line use primary or second rate. 
            if account.exchange_rate_adjustment:
                if account.rate_adjustment == 'secondary':
                    second_rate = True
                else:
                    second_rate = False
            
            #Get exchange_amount, depends of account
            #primary -> sale
            #secondary -> purchase
            copy_context = copy.copy(context)
            copy_context.update({'second_rate':second_rate})
            copy_context.update({'date':exchange_rate_date})
            exchange_amount = res_currency_obj._current_rate(cr, uid, [company_currency.id], exchange_rate_date, arg=None, context=copy_context)[company_currency.id]
   
            account_difference = abs(foreign_balance) * exchange_amount - abs(balance)
                        
            if account_difference > 0.0 and foreign_balance > 0.0 or account_difference < 0.0 and foreign_balance < 0.0:
                total_debit = abs(account_difference)
                total_credit = 0.0
            elif account_difference < 0.0 and foreign_balance > 0.0 or account_difference > 0.0 and foreign_balance < 0.0:
                total_debit = 0.0
                total_credit = abs(account_difference)
            else:
                continue
                
            account = account_account_obj.browse(cr, uid, account_id, context=context)
            move_line = {
                         'name': _('Unreconcile lines adjustment'),
                         'debit': total_debit,
                         'credit': total_credit,
                         'account_id':account_id,
                         'move_id': move.id,
                         'period_id': move.period_id.id,
                         'journal_id': move.journal_id.id,
                         'partner_id': False,
                         'currency_id': account.currency_id.id,
                         'amount_currency': 0.00,
                         'state': 'valid',
                         'company_id': move.company_id.id,
                         }
            new_move_line_id = move_line_obj.create(cr, uid, move_line, context=context)
            lines_created_ids.append(new_move_line_id)
            
        return lines_created_ids
            
    def create_balance_line(self, cr, uid, move, res_user, name, context=None):    
        move_line_obj = self.pool.get('account.move.line')
        amount = self.get_balance_amount(cr, uid, move.id, context=context)
        if amount > 0:
            account_id = res_user.company_id.expense_currency_exchange_account_id.id
            if not account_id:
                raise osv.except_osv(_('Error!'), _('The company have not associated a expense account.\n'))
            credit = amount
            debit = 0.00
        else:
            account_id = res_user.company_id.income_currency_exchange_account_id.id
            if not account_id:
                raise osv.except_osv(_('Error!'), _('The company have not associated a income account.\n'))
            credit = 0.00
            debit = amount * -1    
            
        move_line = {
                             'name': name,
                             'ref': name,
                             'debit': debit,
                             'credit': credit,
                             'account_id': account_id,
                             'move_id': move.id,
                             'period_id': move.period_id.id,
                             'journal_id': move.journal_id.id,
                             'partner_id': False,
                             'currency_id': False,
                             'amount_currency': 0.00,
                             'state': 'valid',
                             'company_id': res_user.company_id.id,
                             }
        new_move_line_id = move_line_obj.create(cr, uid, move_line, context=context)
        return new_move_line_id
    
    def generate_adjustment_move(self, cr, uid, reference, journal, period, exchange_rate_date=False, context=None):
        res_user_obj = self.pool.get('res.users')
        res_user = res_user_obj.browse(cr, uid, uid, context=context)
        name = reference + " " + period.name
        
        if not exchange_rate_date:
            exchange_rate_date = period.date_stop
        
        move_created = {
                    'ref': name,
                    'journal_id': journal.id,
                    'period_id': period.id,
                    'to_check': False,
                    'company_id': res_user.company_id.id,
                    'partner_id': False,
                    'date': exchange_rate_date,
                    }
        
        move_created_id = self.create(cr, uid, move_created)
        move_created = self.browse(cr, uid, move_created_id, context=context)
        
        lines_reconcile_ids = self.create_move_lines_reconcile(cr, uid, move_created, exchange_rate_date, context=context)        
        lines_unreconcile_ids = self.create_move_lines_unreconcile(cr, uid, move_created, period, exchange_rate_date, context=context)
        balance_line_id = self.create_balance_line(cr, uid, move_created, res_user, name, context=context)
        return move_created_id
    
