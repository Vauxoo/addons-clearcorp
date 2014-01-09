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

import time
import pooler
from report import report_sxw
import locale

from openerp.addons.account_report_lib.account_report_base import accountReportbase #Library Base

class Parser(accountReportbase):
    
    def __init__(self, cr, uid, name, context):
        
        super(Parser, self).__init__(cr, uid, name, context=context)
       
        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'storage':{},
            'set_data_template': self.set_data_template,
            'get_move_lines': self.get_move_lines, 
            'sum_debit': self.sum_debit,
            'sum_credit': self.sum_credit,
            'get_journal_list': self.get_journal_list, 
            'return_move_lines':self.return_move_lines,
            'get_format_lang_currency': self.pool.get('account.webkit.report.library').format_lang_currency,      
        })
    
    #set data to use in odt template. 
    def set_data_template(self, cr, uid, data):        
        
        journal_selected = self.get_move_lines(cr, uid, data)
        
        dict_update = {
                       'journal_selected': journal_selected,
                      }
        
        self.localcontext['storage'].update(dict_update)
        return False    
    
    #Receive the journal_ids and return the full object
    def get_journal_list(self, data):
        return self.get_journal_ids(data) #-> list of browse record
    
    #Compute move_lines for all the journals selected
    def get_move_lines(self, cr, uid, data):
        filter_data = []
        journal_selected = {}
        account_library = self.pool.get('account.webkit.report.library')
        
        #******************** Parameters ***************************#
        journal_ids = self.get_journal_ids(data)
        filter_type = self.get_filter(data)                  
        
        if filter_type == 'filter_date':
            start_date = self.get_date_from(data)
            stop_date = self.get_date_to(data)
            
            filter_data.append(start_date)
            filter_data.append(stop_date)
            
        elif filter_type == 'filter_period':
            
            start_period = self.get_start_period(data) #return the period object
            stop_period = self.get_end_period(data)
            
            filter_data.append(start_period)
            filter_data.append(stop_period)
            
        else:
            filter_type = ''
        
        fiscalyear = self.get_fiscalyear(data)
        target_move = self.get_target_move(data)
        
        if self.get_sort_selection(data) == 'date':
            order_by = 'date asc'
        elif self.get_sort_selection(data) == 'name':
            order_by = 'name asc'
            
        #********************************************************#
        
        #Get the move_lines for each journal.
        move_lines = account_library.get_move_lines_journal(cr, 1,
                                                            journal_ids, 
                                                            filter_type=filter_type, 
                                                            filter_data=filter_data, 
                                                            fiscalyear=fiscalyear, 
                                                            target_move=target_move,
                                                            order_by=order_by)
        
        #=======================================================================
        # Group by journal. Return a dictionary where key is journal id  
        # the final result is: {journal_id: [line]}  -> line is a browse record
        #=======================================================================
        for line in move_lines:
            if line.journal_id.id not in journal_selected:
                journal_selected[line.journal_id.id] = []
            
            journal_selected[line.journal_id.id].append(line)
        
        return journal_selected
    
    #Return move_lines that match with journal_id
    def return_move_lines(self, journal_id):
        dict_journal = self.get_data_template('journal_selected')         
        if journal_id in dict_journal.keys():
            move_lines = dict_journal[journal_id]
        else:
            move_lines = []
        
        return move_lines
     
    #Compute debit and credit for move_lines
    def sum_debit(self, journal_id):
        move_lines = self.return_move_lines(journal_id)
        total_debit = 0.0
        result = {}
        
        for line in move_lines:
            total_debit += line.debit
    
        return total_debit
    
    #Compute debit and credit for move_lines
    def sum_credit(self, journal_id):
        total_credit = 0.0
        result = {}
        move_lines = self.return_move_lines(journal_id)
        
        for line in move_lines:
            total_credit += line.credit
    
        return total_credit
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
