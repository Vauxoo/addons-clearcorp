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
import time
from datetime import datetime, timedelta


"""
 @todo: Other options for web_service use currency configuration linked
 the company and they need another configuration based on company.
 This module is based of currency configuration and it unlink the currency 
 from company.
 To return to configuration based on company, you must be require fields in
 company form (see res_company.xml)
 In addition, you must need configurate 'main_currency' parameter that needs
 get_currency_update method.
"""
    
class resCurrencyinherit(orm.Model):
     
    _inherit = 'res.currency'    
    _columns = {
            'automatic_update': fields.boolean('Automatic Update'),
            'second_rate': fields.boolean('Have second rate'),
            'code_rate': fields.char('Code rate', size=64),
            'second_code_rate': fields.char('Second Code Rate', size=64),
            'ir_cron_job_id': fields.many2one('ir.cron', 'Automatic Update Task',),            
            'web_service_associated': fields.selection( 
                                                [                                            
                                                #('Admin_ch_getter','Admin.ch'),
                                                #('ECB_getter','European Central Bank'),
                                                #('NYFB_getter','Federal Reserve Bank of NY'),                                                    
                                                #('Google_getter','Google Finance'),
                                                #('Yahoo_getter','Yahoo Finance '),
                                                #('PL_NBP_getter','Narodowy Bank Polski'),
                                                ('bccr_getter', 'Banco Central de Costa Rica'),  # Added for CR rates
                                                ], "Web-service to use",),
            
            #===================================================================
            #===cron job  fields ===#
            'interval_number': fields.related('ir_cron_job_id', 'interval_number', type='integer', string='Interval Number',help="Repeat every x."),
            'nextcall' : fields.related('ir_cron_job_id', 'nextcall', type='datetime', string='Next Execution Date', help="Next planned execution date for this job."),
            'doall' : fields.related('ir_cron_job_id', 'doall', type='boolean', string='Repeat Missed', help="Specify if missed occurrences should be executed when the server restarts."),
            'interval_type': fields.related('ir_cron_job_id', 'interval_type', type='selection', selection=[('minutes', 'Minutes'), ('hours', 'Hours'), ('work_days','Work Days'), ('days', 'Days'),('weeks', 'Weeks'), ('months', 'Months')], string='Interval Unit'),
            'numbercall': fields.related('ir_cron_job_id', 'numbercall', type='integer', string='Number of Calls', help='How many times the method is called,\na negative number indicates no limit.'),
            #===================================================================
    }
    
    _defaults = {
        'interval_type' : 'days',
    }
    
    #===========================================================================
    # Create a generic method for cron_job creation
    # It could be call from create or write. Create dictionary with 
    # cron_job values
    #===========================================================================
    def cron_job_creation(self, cr, uid, ids=[], vals={}, mode='', context=None):
        res = {}
        #If method is called from write
        if mode == 'write':
            #For write, vals dictionary only have new values (or values with some changes)         
            currency_obj = self.browse(cr, uid, ids, context=context)[0] #Find currency that already exists in database
            name = "Exchanges Rate Cron for currency " + currency_obj.name
           
        elif mode == 'create':
            name = "Exchanges Rate Cron for currency " + vals['name']
        
        #Cron job name. "Clean" name for unnecessary characters. Avoid create
        #name as a tuple.
        name.replace(')','')      
        
        res.update({'name': name})
        
        res.update ({
               'interval_type': 'days',
               'nextcall': time.strftime("%Y-%m-%d %H:%M:%S", (datetime.today() + timedelta(days=1)).timetuple() ), #tomorrow same time
               'interval_number': 1,
               'numbercall': -1,
               'doall': True,
               'model': 'currency.rate.update', 
               'function': 'run_currency_update_bccr',                                              
               'active':True,
               })
        
        return res
    
    #===========================================================================
    """
        @param context: If 'from_ir_cron' key exists, it means that context comes
                        from ir_cron form and write only needs to update state for
                        automatic_update field.
                        
                        If this key doesn't exist in context, keep with the other
                        process.
    """
    def write(self, cr, uid, ids, vals, context=None):
        #For write, vals dictionary only have new values (or values with some changes)
        for currency_obj in self.browse(cr, uid, ids, context=context): #Find currency that already exists in database            
            if 'from_ir_cron' not in context.keys():
                if 'automatic_update' in vals.keys():
                    if vals['automatic_update']: #Check as True
                        if not currency_obj.ir_cron_job_id: #if currency doesn't have a cron associated
                            res = self.cron_job_creation(cr, uid, ids=[currency_obj.id], vals=vals, mode='write', context=context)
                            #include currency_id -> used later for update currency
                            res.update({'args':[currency_obj.id]})
                            #create cron_job
                            cron_job_id = self.pool.get('ir.cron').create(cr, uid, res, context=context)
                            #update currency
                            vals.update({'ir_cron_job_id': cron_job_id})
                        
                        else:
                            update = {}
                            cron_job_id = currency_obj.ir_cron_job_id.id
                            #Extract only values with changes. Update cron job related to currency
                            for key, val in vals.iteritems():
                                #automatic_update is from currency, it won't be included
                                #in values to update from ir.cron.
                                #associate key 'active' in ir.cron object with value in
                                #automatic_update
                                if key not in update.keys() and key != 'automatic_update': 
                                    update[key] = vals[key]                    
                            update.update({'active':vals['automatic_update']})
                            self.pool.get('ir.cron').write(cr, uid, [cron_job_id], update, context=context)
                                                
                    #Don't unlink cron_job. It will pass to inactive state
                    elif currency_obj.ir_cron_job_id:
                        update_cron = {'active': False}
                        self.pool.get('ir.cron').write(cr, uid, [currency_obj.ir_cron_job_id.id], update_cron, context=context)
   
        return super(resCurrencyinherit, self).write(cr, uid, ids, vals, context=context)
    #===========================================================================
    
    def create(self, cr, uid, vals, context={}):  
        cron_job = {}
        #First create currency
        res = super(resCurrencyinherit, self).create(cr, uid, vals, context=context)
        
        #Create cron_job
        if 'automatic_update' in vals.keys():
            cron_job = self.cron_job_creation(cr, uid, ids=[], vals=vals, mode='create', context=context)
            #include currency_id in cron_job
            cron_job.update({'args': [int(res)]})
            #create cron_job
            cron_job_id = self.pool.get('ir.cron').create(cr, uid, cron_job, context=context)
            vals.update({'ir_cron_job_id': cron_job_id})
                
        return res
