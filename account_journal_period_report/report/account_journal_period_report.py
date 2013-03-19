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
from account.report.account_journal import journal_print
from wadllib.application import Parameter
from symbol import parameters

#la herencia se debe hacer de journal_print (clase original del reporte)
#para que se llame el init y el set context, y se puedan usar las variables y métodos.
#si no se hace, se pierden los valores de la clase original donde se está heredando
#la herencia en python se hace pasando por parámetro la clase a heredar (en este caso journal_print)

class account_journal_period_report(journal_print):
    
    def __init__(self, cr, uid, name, context):
        
        super(account_journal_period_report, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_journal_list': self.get_journal_list,  
            'get_format_lang_currency': self.pool.get('account.webkit.report.library').format_lang_currency,  
            'extract_name_move':self.extract_name_move,  
            'cr': cr,  
            'uid': uid,
        })
            
    #Receive the journal_ids and return the full object
    def get_journal_list(self, journal_ids):
        return self.pool.get('account.journal').browse(self.cr, self.uid, journal_ids)     
    
    ''''
    This method is created to solve the error when extracting the name move_id (line.move_id.name) fails because of read permissions
    parameter move_lines are the move_lines that match with the journal and period. Pass from mako. 
    ''' 
    def extract_name_move(self, cr, uid, move_lines):
        move_temp = self.pool.get('account.move')
        dict_name = {} #dict_name keys is the line id. 
        
        for line in move_lines:
            move_id = move_temp.search(cr, uid, [('id', '=', line.move_id.id)])
            move_obj = move_temp.browse(cr, uid, move_id)
            if move_obj[0].name:
                dict_name[line.id] = move_obj[0].name
            else:
                 dict_name[line.id] = move_obj[0].id
        
        return dict_name
            
#the parameters are the report name and module name 
report_sxw.report_sxw( 'report.account_journal_period_print_inherit', 
                       'account.print.journal',
                       'addons/account_journal_period_report/report/account_journal_period_report.mako', 
                        parser = account_journal_period_report)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
