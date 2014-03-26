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
import datetime
import pooler
from report import report_sxw
import locale
from openerp.tools.translate import _

#===============================================================================
# environment variable helper can't be used in odt. Import file where is defined 
# the function, and create a python heritage. With this, the class Parser
# can use embed_logo_by_name method.
#===============================================================================
from openerp.addons.report_webkit.report_helper import WebKitHelper 

class accountReportbase(report_sxw.rml_parse, WebKitHelper):
    
    """
        This class is the base for the reports. Contains all the basic functions
        to extract info that the reports needs
    """
    def __init__(self, cr, uid, name, context):        
        self.cr = cr 
        self.cursor = cr #WebkitHelper use "cursor" instead of "cr"
        self.pool = pooler.get_pool(self.cr.dbname)
       
        super(accountReportbase, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'datetime': datetime, #Necessary to print date and time for print the report. 
            'time': time,
            'cr' : cr,
            'uid': uid,
            'storage':{},
            'get_start_period': self.get_start_period,
            'get_end_period':self.get_end_period,
            'get_fiscal_year':self.get_fiscalyear,
            'get_chart_account_id': self.get_chart_account_id,
            'get_filter': self.get_filter,
            'get_target_move': self.get_target_move,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
            'get_accounts_ids': self.get_accounts_ids,
            'get_journal_ids': self.get_journal_ids,
            'get_partner_ids':self.get_partner_ids,
            'get_historic_strict': self.get_historic_strict,
            'get_special_period': self.get_special_period,
            'display_target_move':self.get_display_target_move,
            'get_display_sort_selection':self.get_display_sort_selection,
            'get_signatures_report': self.get_signatures_report,
            'get_amount_currency':self.get_amount_currency,
            'get_account_base_report':self.get_account_base_report,
            'embed_logo_by_name': self.embed_logo_by_name, #return logo (default_logo) 
            'formatLang': self.formatLang, #return a numeric format for amounts.
            'set_data_template': self.set_data_template,
            'get_data_template': self.get_data_template,
            'get_sort_selection': self.get_sort_selection,
            'get_company_user': self.get_company_user,
         })
    
    #####################################BASIC FUNCTIONS ##############################
    
    #Basic function that extract the id of the wizard and return the object (model)
    
    '''
        The method _get_info return a browse (return the complete model)
    '''
    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field)
        if info:
            return self.pool.get(model).browse(self.cr, self.uid, info)
        return False
    
    '''
        The method _get_form_param return the real value in the wizard. 
    '''
    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)
    
    #########################################################################
    
    def get_start_period(self, data):
        return self._get_info(data,'period_from', 'account.period')
    
    def get_end_period(self, data):
        return self._get_info(data,'period_to', 'account.period')
    
    def get_fiscalyear(self, data):
        return self._get_info(data,'fiscalyear_id', 'account.fiscalyear')
    
    def get_chart_account_id(self, data):
        return self._get_info(data, 'chart_account_id', 'account.account')
    
    def get_filter(self, data):
        return self._get_form_param('filter', data)
    
    def get_target_move(self, data):
        return self._get_form_param('target_move', data)
    
    def get_date_from(self, data):
        return self._get_form_param('date_from', data)

    def get_date_to(self, data):
        return self._get_form_param('date_to', data)
    
    #Case special for conciliation bank -> account_ids is an unicode.
    def get_accounts_ids (self, cr, uid, data):
        if isinstance(data['form']['account_ids'], unicode):
            return self.pool.get('account.account').browse(cr, uid, [int(data['form']['account_ids'])])[0]
        
        return self._get_info(data,'account_ids', 'account.account')
    
    def get_journal_ids(self, data):
        return self._get_info(data, 'journal_ids', 'account.journal')
    
    def get_historic_strict (self, data):
        return self._get_form_param('historic_strict', data)
    
    def get_special_period (self, data):
        return self._get_form_param('special_period', data)
    
    def get_amount_currency (self, data):
        return self._get_form_param('amount_currency', data)
    
    def get_account_base_report(self, data):
        return self._get_info(data, 'account_base_report', 'account.financial.report')
    
    def get_sort_selection(self, data):
        return self._get_form_param('sort_selection', data)
    
    def get_partner_ids(self, data):
        return self._get_info(data, 'res_partners_ids', 'res.partner')    

    ################################## INFO DISPLAY ###########################
    
    def get_display_target_move(self, data):
        val = self._get_form_param('target_move', data)
        if val == 'posted':
            return _('All Posted Entries')
        elif val == 'all':
            return _('All Entries')
        else:
            return val
    
    def get_display_sort_selection(self, data):
        val = self._get_form_param('sort_selection', data)
        if val == 'date':
            return _('Date')
        elif val == 'name':
            return _('Name')
        else:
            return val
       
    ##################### SIGNATURES ############################
     #Return the users that can sign the report.
    def get_signatures_report(self, cr, uid, report_name):  
      report_id = self.pool.get('ir.actions.report.xml').search(cr, uid,[('name','=', report_name)])
      report_obj = self.pool.get('ir.actions.report.xml').browse(cr, uid, report_id)
      return report_obj[0].signature_users
  
    ################### IMAGE MANIPULATION ######################        
    #Use get_logo_by_name function from report_helper. Return img, a binary image. 
    def embed_logo_by_name(self, name):
        img, type = self.get_logo_by_name(name)
        
        return img 
    
    #================ SET AND GET DATA INTO A AEROO REPORT TEMPLATE ===========#
    #===========================================================================
    # This method will be re-implemented in each report that needs some 
    # temporary variable in odt/ods templates. set_data_template will include 
    # in the parsers and it will include values and variables that the report 
    # needs. 
    #===========================================================================
    
    #===============================================================================
    #    get_data_template set_data_template and methods are used to create a workarround 
    #    (not found a way to have temporary variables in a template in aeroo). 
    #    The set method calls the methods that do the calculations and stores them 
    #    in a dictionary that is built into the localcontext, called storage. 
    #    All values ​​are stored in this dictionary.
    # 
    #    Then get_data_template method that receives a string, which is the key of the dictionary, 
    #    pass the value of the key we want and this method returns the value stored in this key.
    # 
    #    Set_data_template method is called in the template if odt as follows: 
    #    <if test="set_data_template(cr, uid, data)"> </if>. 
    #    In this way, we obtain the values ​​and can work with them directly in the template odt,
    #     shaped <get_data_template('key')>.
    #===============================================================================
    
    def set_data_template(self, cr, uid, data):        
        
        dict_update = {}
        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #get data with a specific key
    """@param key: key is a string. It's comming for the odt template and return the value that match with key in storage dictionary """
    def get_data_template(self, key):
        if key in self.localcontext['storage'].keys():
            return self.localcontext['storage'][key]
        return False
    
    #### METHODS TO DISPLAY INFO, BUT DATA DOESN'T COME FROM A WIZARD ####
    def get_company_user(self, cr, uid):
        user = self.pool.get('res.users').browse(cr, uid, uid)

        return self.pool.get('res.company').browse(cr, uid, user.company_id.id)
        
        
        
        