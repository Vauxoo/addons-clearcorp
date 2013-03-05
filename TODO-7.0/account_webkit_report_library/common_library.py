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

import copy
import netsvc
from osv import fields, orm
import tools
from tools.translate import _

class AccountWebkitReportLibrary(orm.Model):
    _name =  "account.webkit.report.library"
    _description = "Account Webkit Reporting Library"
    
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
        
    def get_move_lines(self, cr, uid, account_ids, filter_type='', filter_data=None, fiscalyear=None, target_move='all', unreconcile = False, historic_strict=False, special_period =False, context=None):
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
         
        '''
        #TODO: Translate comments to english
        """
            Cambio realizado el 9 de enero de 2012 (Diana Rodriguez)
            
            Anteriormente, el método get_move_lines (del objeto account.webkit.report.library, librería estándar de los reportes, 
            sólo se utilizaba en el reporte de Conciliación bancaria. El reporte de conciliación bancaria no recibe el período de inicio
            por lo que el método de get_move_lines no contempla el período de inicio, necesario en el reporte de saldo de cuenta de bancos.
            Se realiza el cambio tanto en el reporte de conciliación bancaria para que el período inicial no se tome en cuenta (inicializado en None)
            y en la librería se especifica que si se encuentra en None no lo tome en cuenta y que si trae información lo utilice dentro del filtro
            para sacar el rango de periodos que se digita en el wizard. 
            
            Se modifica tanto el reporte de conciliación bancaria, como la librería, para que el método funcione solamente con un período final o bien
            con un rango de períodos, como trabaja el reporte de saldo de cuenta de bancos. 
            
            Para el caso de las fechas, se trabaja de la misma forma. (El saldo de cuentas de bancos si toma la fecha de inicio)
      
            Para eliminar la secuencias de ifs, se construye un dominio para pasárselo una única vez y realizar el llamado de la búsqueda de las
            líneas. 
        """
           
        account_obj = self.pool.get('account.account')
        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = []
        list_tuples = []
       
        #los dominios se construyen de una lista con tuplas. Se arma el dominio que se necesita.
        #EL DOMINIO QUE SE CONSTRUYE ES PARA EL OBJETO account.move.line (sacar las líneas que coincidan 
        #con el dominio final) 
        
        #*******************************CONSTRUCCION DE DOMINIO DE BUSQUEDA ***************************#
        #si para los campos filter_data, filter_type no hay datos y el año fiscal no existe
        #se sacan las cuentas con los ids y el target_move seleccionado.        
        #********account_ids ******#
        domain = ('account_id', 'in', account_ids)
        list_tuples.append(domain)        
        
        #********target_mvove ******#
        if not target_move == 'all':
            domain = ('move_id.state', '=', target_move)
            list_tuples.append(domain)        
        
        #********Filter by date, period or filter_type = '' *********#
        if filter_type == 'filter_date':
            if filter_data[0] is None: #si solamente se toma la fecha final para sacar el reporte.
                date_stop = filter_data[1]
                domain = ('date', '<=', date_stop)
                list_tuples.append(domain)
            else:
                domain_start_date = ('date', '>=', filter_data[0])
                domain_stop_date = ('date', '<=', filter_data[1])
                list_tuples.append(domain_start_date)
                list_tuples.append(domain_stop_date)                

        elif filter_type == 'filter_period':
            period_domain_list = []
            date_stop = ('date_stop', '<=', filter_data[1].date_stop)
            period_domain_list.append(date_stop)
            #Se debe tomar en cuenta el año fiscal y si es especial o no.
            if fiscalyear:
                fiscal_year = ('fiscalyear_id', '=', fiscalyear.id)
                period_domain_list.append(fiscal_year)
            if special_period == False:
                special = ('special', '=', False)
            else:
                special = ('special', '=', True)
            period_domain_list.append(special)
            
            if filter_data[0]: 
                #el reporte de saldo de bancos si toma el período de inicio 
                date_start = ('date_start', '>=', filter_data[0].date_start)
                period_domain_list.append(date_start)
            
            #al final toma en cuenta año fiscal, periodos especiales y los períodos de inicio y fin           
            periods_ids = self.pool.get('account.period').search(cr, uid,period_domain_list, context=context)
                
            #se obtienen los períodos con los ids anteriores.
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
        
        #si no existe el filtro, pero existe el año fiscal se sacan los periodos que coincidan con ese año.
        #el parámetro special indica si se deben tomar o no encuenta períodos especiales del año fiscal.
        elif filter_type == '' and fiscalyear:
            if special_period is True:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', True),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            else:
                periods_ids = self.pool.get('account.period').search(cr, uid, [('special', '=', False),('fiscalyear_id', '=', fiscalyear.id)], context=context)
            domain_period = ('period_id.id', 'in', periods_ids)
            list_tuples.append(domain_period)
                
        #**********************************************************************************************#
        
        if unreconcile == False:
            move_line_ids = move_line_obj.search(cr, uid, list_tuples, context=context)
                
        else:
            #list_tuples + [domain_unreconciled] -> Con esta sintaxis no se altera la variable 
            #list_tuples, el + hace una lista completa con la variable domain_unreconciled. Se
            #deben agregar los [] para que quede con formato de lista.
            
            #Primero se sacan los ids de las lineas no conciliadas.
            domain_unreconciled = ('reconcile_id', '=', None)      
            unreconciled_move_line_ids = move_line_obj.search(cr, uid, list_tuples + [domain_unreconciled], context=context)
            
            #historic_strict si se requiere un corte histórico extricto en la conciliación
            #si no se obtienen las lineas que estan sin conciliar a la fecha en la que se solicita
            #el reporte.  
            if historic_strict == False:
                move_line_ids = unreconciled_move_line_ids
            else: 
                #Se obtiene la fecha máxima de conciliación, para obtener como parámetro de donde 
                #sacar las lineas  
                if filter_type == 'filter_date':
                    #la fecha máxima es la fecha final seleccionada
                    max_reconciled_date = filter_data[1]    
                elif filter_type == 'filter_period':
                    #la fecha máxima es la fecha final del período seleccionado
                    max_reconciled_date = filter_data[1].date_stop
                elif fiscalyear:
                    #si existe año fiscal, se saca la fecha final del año fiscal
                    max_reconciled_date = fiscalyear.date_end
                else:
                    max_reconciled_date = False
                
                #Si existe una fecha máxima seleccionada, se sacan las líneas sin conciliar.
                #esto es para comparar las líneas conciliadas con las líneas sin conciliar.
                #si existe alguna linea sin conciliar que sea mayor a la fecha máxima de conciliación,
                #se debe agregar como una línea sin conciliar.
                if max_reconciled_date:
                    domain_reconciled = ('reconcile_id', '<>', None)  
                    reconciled_move_line_ids = move_line_obj.search(cr, uid, list_tuples + [domain_reconciled], context=context)
                    reconciled_move_lines = move_line_obj.browse(cr, uid, reconciled_move_line_ids, context=context)
                    for line in reconciled_move_lines:
                        if line.reconcile_id:
                            if line.reconcile_id.create_date > max_reconciled_date:
                                unreconciled_move_line_ids.append(line.id)
                    
                move_line_ids = unreconciled_move_line_ids
              
        move_lines = move_line_ids and move_line_obj.browse(cr, uid, move_line_ids, context=context) or []
        
        return move_lines
    
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
                            filter_type = '',
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
        filter_type:        string, tipo de filtro seleccionado.
        
        If there is an end_period without a start_period, all precedent moves for the end period will be used.
        If there isn't a fiscal year, all open fiscal years will be used. To include all closed fiscal years, the all_fiscal_years must be True.
        '''
        account_obj = self.pool.get('account.account')
        period_obj = self.pool.get('account.period')
        context_copy = copy.copy(context)
        context = {}
        
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
        if journal_ids:
            context.update({'journal_ids':journal_ids})
        if chart_account_id:
            context.update({'chart_account_id':chart_account_id})
                
        """
        TODO: Translate to english
        @author: Diana Rodríguez - Clearcorp
        Cambio realizado el 1 de febrero de 2012: 
            La variable initial_balance establece si estamos pidiendo un balance inicial (Valor en True). Si es false, pedimos un balance "corriente"
            Si solicitamos un balance inicial existen dos opciones:
                con un rango de dos períodos: Se obtiene el anterior al período inicial seleccionado que coincida con el año fiscal. Este es el end_period_id
                con solamente el período final: Se obtiene una lista de períodos hasta el período final, se pasa como el period_ids. El end_period_id es el de apertura
            
            Si solicitamos un balance "corriente" existen dos opciones:
                Si son dos, se obtiene la lista de periodos y el año fiscal
                Si solo es el end_period: El año fiscal y el end_period_id es el que se selecciona.                
        """
        
        #fiscal_year        
        fiscal_year = self.pool.get('account.fiscalyear').browse(cr,uid,fiscal_year_id)
        
        if start_period_id:
            start_period = self.pool.get('account.period').browse(cr,uid,start_period_id)
        if end_period_id:
            end_period = self.pool.get('account.period').browse(cr,uid,end_period_id)
                    
        #Si el filtro es periodos
        if filter_type == 'filter_period':
            #se solicita el balance inicial
            if initial_balance == True:
                #si se tienen los dos períodos -> Se calcula la lista de períodos hasta el periodo inicial seleccionado. El start_period_id es el periodo
                #anterior al periodo inicial seleccionado.
                if start_period_id and end_period_id:
                    start_period_id = self.get_start_previous_period(cr, uid, start_period=start_period, fiscal_year=fiscal_year)
                    start_period = self.pool.get('account.period').browse(cr, uid, start_period_id)
                    period_ids = self.get_interval_period(cr, uid, start_period=start_period, end_period = end_period, fiscal_year=fiscal_year_id, initial_balance=True)
                    
                #Si solamente se selecciona el periodo final -> se obtiene el rango de períodos hasta el final. 
                #el end_period_id = El periodo de apertura más "antiguo"
                if (not start_period_id and end_period_id):
                    period_ids = self.get_interval_period(cr, uid, end_period=end_period, fiscal_year=fiscal_year_id,initial_balance=True)
                    
            #Si se quiere un balance corriente
            else:
                #solamente se selecciona un periodo : Periodo final
                if not period_ids and fiscal_year_id and not start_period_id and end_period_id:
                    end_period = period_obj.browse(cr, uid, end_period_id)
                    period_ids = period_obj.search(cr, uid, ['&',('fiscalyear_id','=',fiscal_year_id),('date_stop', '<=', end_period.date_stop)], context=context)
                
                #Se seleccionan ambos periodos
                if not period_ids and fiscal_year_id and start_period_id and end_period_id:
                    start_period = period_obj.browse(cr, uid, start_period_id)
                    end_period = period_obj.browse(cr, uid, end_period_id)
                    period_ids = self.get_interval_period(cr, uid, start_period=start_period, end_period=end_period, fiscal_year=fiscal_year_id)
                
                #solamente en balance "corriente" se necesita el periodo inicial
                if start_period_id:
                    context.update({'period_from':start_period_id})
        
        #Si no existen filtros, se busca el primer periodo especial del año fiscal          
        if filter_type == '':       
            if initial_balance:
                period_ids = [self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',fiscal_year_id),('special','=',True)],order='date_start asc')[0]]
            else:
                period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=', fiscal_year_id)] )        
        
        #####################################################################
        
        if end_period_id:
            context.update({'period_to':end_period_id})
        
        if period_ids:
            context.update({'periods':period_ids})
        
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
        
    def get_balance_tmp(self, cr, uid, account_ids, field_names, arg=None, context=None,
                    query='', query_params=()):
        ''' Get the balance for the provided account ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        'context': The context have the filters for the move lines, to see the proper keys and values that should be used check
                   the method _query_get of account_move_line
        '''
        account_obj = self.pool.get('account.account')
        
        res = account_obj._account_account__compute(cr, uid, account_ids, field_names, arg=arg, context=context,
                    query=query, query_params=query_params)
        
        return res

    def get_account_child_ids(self, cr, uid, account_ids, context={}):
        print account_ids
        if isinstance(account_ids, orm.browse_record):
            account_ids = [account_ids.id]
        elif isinstance(account_ids, int):
            account_ids = [account_ids]
        return self.pool.get('account.account')._get_children_and_consol(cr, uid, account_ids, context=context)
        
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
        
    #devuelve el monto de la moneda más el símbolo en la posición que se indica    
    def format_lang_currency (self, cr, uid, amount_currency, currency):
        format_currency = ''
        
        if currency:
           if currency.symbol_prefix:
                format_currency =  currency.symbol_prefix + ' ' + amount_currency
           else:
                format_currency = amount_currency+ ' ' +  currency.symbol_sufix
        else:
            format_currency = amount_currency
            
        return format_currency  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
