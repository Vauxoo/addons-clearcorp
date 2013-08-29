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

from osv import fields, orm, osv
from tools.translate import _

class toolsModulesextendedAccountFinancialReport(orm.Model):
    """
        This class extend functions of account.financial.report model.
    """  
    _name = "account.financial.report"
    _inherit = "account.financial.report"
    
    _columns = {
        'account_type': fields.many2many('account.financial.report.type', 'account_financial_report_type_rel', string = "Base Catalog Account Type"),
     }

class toolsModulesextendedAccount(orm.Model):

    """
        This class extend functions of account.account model.
    """    
    
    _name = "account.account"
    _inherit = "account.account"
        
    _columns = {
        'report_currency_id': fields.many2one('res.currency', 'Report Currency', help="Currency to show in the reports."),
    }


class toolsModulesextendedAccountPeriod(orm.Model):

    """
        This class extend functions of account.period model.
    """    
    _name = "account.period"
    _inherit = "account.period"    
    
    """
        @param start_period: Initial period, can be optional in the filters
        @param end_period: Final period, is required
        @param fiscal_year: Fiscal year, is required
        @return: A id list of periods
    
        All of param are objects
    """
    
    def get_interval_period (self, cr, uid, start_period=None, end_period=None, fiscal_year=None, initial_balance=False):
        
        period_obj = self.pool.get('account.period')
        period_list = []
        
        #si se solicita el intervalo para obtener el balance inicial
        if initial_balance:
            if start_period and end_period:
                #el start_period_id es el periodo anterior al escogido
                period_list = period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscal_year),('date_stop','<=',start_period.date_stop)])
            
            elif not start_period and end_period:
                #se busca el primer periodo especial del año
                period_list = period_obj.search(cr, uid, [('fiscalyear_id','=',fiscal_year),('special','=',True)],order='date_start asc')[0]
        
        #si es un balance "corriente"
        else:
            if start_period and end_period:
                #se buscan los periodos que coincidan con el intervalo
                period_list =  period_obj.search(cr, uid, [('fiscalyear_id','=',fiscal_year), ('date_start','>=',start_period.date_start),('date_stop','<=',end_period.date_start)])
            
            elif not start_period and end_period:
                #todos los periodos hacia "atras" del periodo final
                period_list = period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscal_year),('date_stop','<=',end_period.date_stop)])
                
        return period_list
    
    """
        @param start_period: Initial period, can be optional in the filters
        @param end_period: Final period, is required
        @param fiscal_year: Fiscal year, is required
        @return: The previous period for start_period
        All of param are objects
    """              
    def get_start_previous_period(self, cr, uid, start_period=None, fiscal_year=None):
        
        account_period_obj = self.pool.get('account.period')
        
        pevious_period = account_period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscal_year.id), ('date_stop', '<', start_period.date_stop)], order='date_stop DESC')[0]
       
        return pevious_period
    
    ############################ METHOD THAT USED THE PERIOD AS PRINCIPAL REFERENCE ################
    #Openning period for fiscal year take the selected period as reference.
    def get_opening_period(self, cr, uid, select_period, context=None):
        fiscalyear = select_period.fiscalyear_id
        period_obj = self.pool.get('account.period')
        opening_period_id = period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear.id),('special','=',True)], order='date_start asc', context=context)[0]
        opening_period = period_obj.browse(cr, uid, opening_period_id, context=context)
        return opening_period


    #Last period of fiscal year when the period is not special and take the fiscalyear as reference
    def get_last_period_fiscalyear(self, cr, uid, fiscalyear):
        account_period_obj = self.pool.get('account.period')
        period_ids = account_period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear.id), ('special', '=', False)])
        periods = account_period_obj.browse(cr, uid, period_ids)
        period_select = periods[0]
        for current_period in periods:
            if current_period.date_start > period_select.date_start:
                period_select = current_period
        return period_select
    
    #Last period of fiscal year when the period is not special and take the start_period as reference
    def get_last_period(self, cr, uid, start_period):
        account_period_obj = self.pool.get('account.period')
        period_ids = account_period_obj.search(cr, uid, [('fiscalyear_id', '=', start_period.fiscalyear_id.id), ('special', '=', False)])
        periods = account_period_obj.browse(cr, uid, period_ids)
        period_select = start_period
        for period in periods:
            if (period.date_start < start_period.date_start and period.date_start > period_select.date_start) or (period.date_start < start_period.date_start and start_period == period_select):
                period_select = period
        if period_select == start_period:
            fiscalyear = start_period.fiscalyear_id
            fiscalyear_select = fiscalyear
            account_fiscalyear_obj = self.pool.get('account.fiscalyear')
            all_fiscalyears_ids = account_fiscalyear_obj.search(cr, uid, [])
            all_fiscalyears = account_fiscalyear_obj.browse(cr, uid, all_fiscalyears_ids)
            for current_fiscalyear in all_fiscalyears:
                if (current_fiscalyear.date_start < fiscalyear.date_start and current_fiscalyear.date_start > fiscalyear_select.date_start) or (current_fiscalyear.date_start < fiscalyear.date_start and fiscalyear == fiscalyear_select):
                    fiscalyear_select = current_fiscalyear
            if fiscalyear_select == fiscalyear:
                #raise osv.except_osv(_('Error fiscal year'),_('There is no previous period to compare'))
                period_select = start_period
            else:
                period_select = self.get_last_period_fiscalyear(cr, uid, fiscalyear_select)
        return period_select
    
    ############################ METHOD THAT USED THE FISCAL YEAR AS PRINCIPAL REFERENCE ################
    
    #Method that return the first and last period, take as reference the fiscal year, the order
    #determinate if wants the first (ASC) or last (DESC)
    #Can change if need the special or not (special parameter)
    def get_first_last_fiscalyear_period(self, fiscalyear, special=False, order='ASC'):
        period_obj = self.pool.get('account.period')
        p_id = period_obj.search(self.cursor,
                                 self.uid,
                                 [('special','=', special),
                                  ('fiscalyear_id', '=', fiscalyear.id)],
                                 limit=1,
                                 order='date_start %s' % (order,))
        if not p_id:
            raise osv.except_osv(_('No period found'),'')
        return period_obj.browse(self.cursor, self.uid, p_id[0])