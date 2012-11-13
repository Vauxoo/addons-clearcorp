#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import netsvc
from osv import fields, orm
import tools
from tools.translate import _

class AccountWebkitReportLibrary(orm.Model):
    _name =  "account.webkit.report.library"
    _description = "Account Webkit Reporting Library"
        
    def get_move_lines(self, cr, uid, account_ids, filter_type='', filter_data=None, fiscalyear=None, target_move='all', unreconcile = False, historic_strict=False, context=None):
        ''' Get the move lines of the accounts provided and filtered.
        Arguments:
        'account_ids': List of accounts ids.
        'filter_type': Filter used, possibles values: 'filter_date', 'filter_period' or ''.
        'filter_data': If filter is by date then filter_data is a list of strings with the initial date and the ending date, if filter is by period then
                       filter_data is a list of browse record with the initial period and the ending period.
        'fiscalyear':  Browse record of the fiscal year selected.
        'target_move': Target moves of the report, possibles values: 'all' or 'posted'.
        'unreconcile': If True then get the move lines unreconciled.
        'historic_strict': Used when unreconcile = True, forces to include move lines that where not reconciled at the end date of the filter but are now.
         Armando was here.
        '''
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        move_lines_ids = []
        
        if unreconcile == False:
            if target_move == 'all':
                if filter_type == '' and filter_data == None and fiscalyear == None:
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids)], context=context)
                elif filter_type == 'filter_date':
                    date_stop = filter_data[1]
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop)], context=context)
                elif filter_type == 'filter_period':
                    periods_ids = self.pool.get('account.period').search(cr, uid, [('date_stop', '<=', filter_data[1].date_stop)])
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('period_id.id', 'in', periods_ids)], context=context)
                elif filter_type == '' and fiscalyear != None:
                    date_stop = fiscalyear.date_stop
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop)], context=context)
            elif target_move == 'posted':
                if filter_type == '' and filter_data == None and fiscalyear == None:
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('move_id.state', '=', 'posted')], context=context)
                elif filter_type == 'filter_date':
                    date_stop = filter_data[1]
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('move_id.state', '=', 'posted')], context=context)
                elif filter_type == 'filter_period':
                    periods_ids = self.pool.get('account.period').search(cr, uid, [('date_stop', '<=', filter_data[1].date_stop)])
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('period_id.id', 'in', periods_ids), ('move_id.state', '=', 'posted')], context=context)
                elif filter_type == '' and fiscalyear != None:
                    date_stop = fiscalyear.date_stop
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('move_id.state', '=', 'posted')], context=context)
        else:
            if target_move == 'all':
                if filter_type == '' and filter_data == None and fiscalyear == None:
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('reconcile_id', '=', False)], context=context)
                elif filter_type == 'filter_date':
                    date_stop = filter_data[1]
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('reconcile_id', '=', False)], context=context)
                    if historic_strict:
                        move_line_ids = move_line_ids + self.get_move_lines_unconciled(cr, uid, account_ids, filter_type=filter_type, filter_data=filter_data, context=context)
                elif filter_type == 'filter_period':
                    periods_ids = self.pool.get('account.period').search(cr, uid, [('date_stop', '<=', filter_data[1].date_stop)])
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('period_id.id', 'in', periods_ids), ('reconcile_id', '=', False)], context=context)
                    if historic_strict:
                        move_line_ids = move_line_ids + self.get_move_lines_unconciled(cr, uid, account_ids, filter_type=filter_type, filter_data=filter_data, context=context)
                elif filter_type == '' and fiscalyear != None:
                    date_stop = fiscalyear.date_stop
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('reconcile_id', '=', False)], context=context)
                    if historic_strict:
                        move_line_ids = move_line_ids + self.get_move_lines_unconciled(cr, uid, account_ids, fiscalyear=fiscalyear, context=context)
            elif target_move == 'posted':
                if filter_type == '' and filter_data == None and fiscalyear == None:
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('move_id.state', '=', 'posted'), ('reconcile_id', '=', False)], context=context)
                elif filter_type == 'filter_date':
                    date_stop = filter_data[1]
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('move_id.state', '=', 'posted'), ('reconcile_id', '=', False)], context=context)
                    if historic_strict:
                        move_line_ids = move_line_ids + self.get_move_lines_unconciled(cr, uid, account_ids, filter_type=filter_type, filter_data=filter_data, context=context)
                elif filter_type == 'filter_period':
                    periods_ids = self.pool.get('account.period').search(cr, uid, [('date_stop', '<=', filter_data[1].date_stop)])
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('period_id.id', 'in', periods_ids), ('move_id.state', '=', 'posted'), ('reconcile_id', '=', False)], context=context)
                    if historic_strict:
                        move_line_ids = move_line_ids + self.get_move_lines_unconciled(cr, uid, account_ids, filter_type=filter_type, filter_data=filter_data, context=context)
                elif filter_type == '' and fiscalyear != None:
                    date_stop = fiscalyear.date_stop
                    move_line_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('move_id.state', '=', 'posted'), ('reconcile_id', '=', False)], context=context)
                    if historic_strict:
                        move_line_ids = move_line_ids + self.get_move_lines_unconciled(cr, uid, account_ids, fiscalyear=fiscalyear, context=context)
            
        move_lines = move_line_ids and move_line_obj.browse(cr, uid, move_line_ids) or []
        
        return move_lines
    
    def get_move_lines_unconciled(self, cr, uid, account_ids, filter_type='', filter_data=None, fiscalyear=None, context=None):
        ''' Get the move lines reconciled that their date is greater than the filter given. 
        Arguments:
        'account_ids': List of accounts ids.
        'filter_type': Filter used, possibles values: 'filter_date', 'filter_period' or ''.
        'filter_data': If filter is by date then filter_data is a list of strings with the initial date and the ending date, if filter is by period then
                       filter_data is a list of browse record with the initial period and the ending period.
        'fiscalyear':  Browse record of the fiscal year selected.
        '''
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        move_reconcile_obj = self.pool.get('account.move.reconcile')
        move_lines_conciled_ids = []
        move_lines_ids = []
                
        if filter_type == 'filter_date':
            date_stop = filter_data[1]
            move_lines_conciled_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('reconcile_id', '!=', False)], context=context)
        elif filter_type == 'filter_period':
            periods_ids = self.pool.get('account.period').search(cr, uid, [('date_stop', '<=', filter_data[1].date_stop)])
            move_lines_conciled_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('period_id.id', 'in', periods_ids), ('reconcile_id', '!=', False)], context=context)
        elif filter_type == '' and fiscalyear != None:
            date_stop = fiscalyear.date_stop
            move_lines_conciled_ids = move_line_obj.search(cr, uid, [('account_id', 'in', account_ids), ('date', '<=', date_stop), ('reconcile_id', '!=', False)], context=context)
            
        move_lines_conciled = move_lines_conciled_ids and move_line_obj.browse(cr, uid, move_lines_conciled_ids) or []
        
        for move_line_conciled in move_lines_conciled:
            move_reconcile = move_line_conciled.reconcile_id
            for line in move_reconcile.line_id:
                if filter_type == 'filter_period':
                    if line.period_id.id not in periods_ids:
                        move_lines_ids.append(move_line_conciled.id)
                        break
                else:
                    if line.date >= date_stop:
                        move_lines_ids.append(move_line_conciled.id)
                        break
                    
        return move_lines_ids
    
    def get_account_balance(self, cr, uid,
                            account_ids,
                            field_names,
                            initial_balance=False,
                            company_id=False,
                            fiscal_year_id=False,
                            all_fiscal_years=False,
                            state='all',
                            start_date=False,
                            end_date=False,
                            start_period_id=False,
                            end_period_id=False,
                            period_ids=False,
                            journal_ids=False,
                            chart_account_id=False,
                            context={}):
        ''' Get the balance for the provided account ids with the provided filters
        Arguments:
        account_ids:        [int], required, account ids
        field_names:        ['balance', 'debit', 'credit', 'foreign_balance'], the fields to compute
        initial_balance:    bool, True if the return must be the initial balance for the period of time specified, not the ending balance.
        company_id:         int, id for the company
        fiscal_year_id:     int, id for the fiscal year
        all_fiscal_years:   bool, True if all fiscal years must be used, including the closed ones. (usefull for receivable for ex.)
        state:              selection of: draft, posted, all; the state of the move lines used in the calculation
        start_date:         date string, start date
        end_date:           date string, end date
        start_period_id:    int, start period id
        end_period_id:      int, end period id
        period_ids:         list of int, list of periods ids used
        journal_ids:        list of int, list of journal ids used
        chart_account_id:   int, chart of account used
        
        If there is an end_period without a start_period, all precedent moves for the end period will be used.
        If there isn't a fiscal year, all open fiscal years will be used. To include all closed fiscal years, the all_fiscal_years must be True.
        '''
        account_obj = self.pool.get('account.account')
        context_copy = context.copy()
        context = {}
        if initial_balance:
            context.update({'initial_bal':initial_balance})
        if company_id:
            context.update({'company_id':company_id})
        if fiscal_year_id:
            context.update({'fiscalyear':fiscal_year_id})
        if all_fiscal_years:
            context.update({'all_fiscalyear':all_fiscal_years})
        if state:
            context.update({'state':state})
        if start_date:
            context.update({'date_from':start_date})
        if end_date:
            context.update({'date_to':end_date})
        if start_period_id:
            context.update({'period_from':start_period_id})
        if end_period_id:
            context.update({'period_to':end_period_id})
        if period_ids:
            context.update({'periods':period_ids})
        if journal_ids:
            context.update({'journal_ids':journal_ids})
        if chart_account_id:
            context.update({'chart_account_id':chart_account_id})
        '''
        Description for the __compute method:
        Get the balance for the provided account ids with the provided filters
        Arguments:
        `account_ids`: list, account ids
        `field_names`: list, the fields to compute (valid values:
                       'balance', 'debit', 'credit', foreign_balance)
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        'context': The context have the filters for the move lines, to see the proper keys and values that should be used check
                   the method _query_get of account_move_line
                   initial_bal:         bool, True if the return must be the initial balance for the period of time specified, not the ending balance.
                   company_id:          int, id for the company, if provided only moves for that company will be used
                   fiscalyear:          int, id for the fiscal year, if provided only moves for that fiscal year will be used
                   all_fiscalyear:      bool, True if all fiscal years must be used, including the closed ones. (usefull for receivable for ex.)
                   state:               selection of: draft, posted, all; the state of the move lines used in the calculation
                   date_from:           date string, start date
                   date_to:             date string, end date
                   period_from:         int, start period id
                   period_to:           int, end period id
                   periods:             list of int, list of periods ids used
                   journal_ids:         list of int, list of journal ids used
                   chart_account_id:    int, chart of account used
        '''
        res = account_obj._account_account__compute(cr, uid, account_ids, field_names, context=context)
        context = context_copy
        
        return res

    def get_account_child_ids(self, cr, uid, account_ids, context={}):
        ids = []
        if isinstance(account_ids, list):
            ids = account_ids
        else:
            ids = [account_ids]
        return _get_children_and_consol(cr, uid, account_ids, context=context)
        
    def get_category_accounts(self, cr, uid, company_id):
        account_account_obj = self.pool.get('account.account')
        res_company_obj = self.pool.get('res.company')
        company = res_company_obj.browse(cr, uid, company_id)
        if company:
            asset_category_account_id = company['property_asset_view_account']
            liability_category_account_id = company['property_liability_view_account']
            equity_category_account_id = company['property_equity_view_account']
            income_category_account_id = company['property_income_view_account']
            expense_category_account_id = company['property_expense_view_account']
        return {
            'asset':        asset_category_account_id,
            'liability':    liability_category_account_id,
            'equity':       equity_category_account_id,
            'income':       income_category_account_id,
            'expense':      expense_category_account_id,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
