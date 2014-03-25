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
import pooler
import time
from datetime import datetime, timedelta
import netsvc
import string
from tools.translate import _
import logging

class resCurrencyrateInherit(orm.Model):
    _inherit = "res.currency.rate"
    
    _columns = {
        'second_rate': fields.float('Second Rate', digits=(12,6), help="The second rate of the currency of rate 1")
    }


class currencyRateupdate(orm.Model):
    """Class that handle an ir.cron call who will update currencies based on a web url"""
    _inherit = "currency.rate.update"
    
    logger2 = logging.getLogger('currency.rate.update')
    logger = netsvc.Logger()
    LOG_NAME = 'cron-rates'
    MOD_NAME = 'c2c_currency_rate_update: '
    
    """
    @param arg1: Comes from cron_job. It's currency_id associated to update 
                 service. With this id, we can obtain all information about
                 cron_job associated and currency.
    """
    def run_currency_update_bccr(self, cr, uid, arg1=None):

        curr_obj = self.pool.get('res.currency')
        rate_obj = self.pool.get('res.currency.rate')
        
        #=======Currency to update
        #Find currency 
        currency_id = curr_obj.browse(cr, uid,[arg1],context=None)[0]
        #Find service associated to currency
        service = currency_id.web_service_associated
              
        #========Base currency
        res_currency_base_id = curr_obj.search(cr, uid, [('base', '=', True)])
        res_currency_base = curr_obj.browse(cr, uid, res_currency_base_id)[0]
        
        factory = Currency_getter_factory()
        try :
             #Initialize service class
             getter = factory.register(service)
             #get_update_currency return a dictionary with rate and name's currency 
             #receive a array with currency to update
             res_sale, res_purchase, log_info = getter.get_updated_currency(cr, uid, [currency_id.name], '') #main_currency for this method is not necessary
                
             #In res_currency_service, name is date when the rate is updated
             for date, rate in res_sale[currency_id.name].iteritems():                
                rate_ids = rate_obj.search(cr, uid, [('currency_id','=',currency_id.id),('name','=',date)])
                if not len(rate_ids):
                     #sale rate
                     rate = float(rate)
                     if currency_id.sequence > res_currency_base.sequence:
                         rate = 1.0/float(rate)
                     vals = {'currency_id': currency_id.id, 'rate': rate, 'name': datetime.strptime(date,"%Y-%m-%d")}
                     
                     #purchase rate
                     if currency_id.second_rate: #check if currency has second_rate activated option
                         second_rate = res_purchase[currency_id.name][date]
                         if currency_id.sequence > res_currency_base.sequence:
                             second_rate = 1.0/float(second_rate)
                         vals.update({'second_rate': second_rate}) 
                     else:
                        vals.update({'second_rate': 0.0})                     
                     
                     x = rate_obj.create(cr, uid, vals)
                     
             note = "Currency sale and purchase rate " + currency_id.name + " updated at %s "\
                %(str(datetime.today()))
             
             self.logger.notifyChannel(self.LOG_NAME, netsvc.LOG_INFO, str(note))
            
        except Exception, e:
             error_msg = "Error!" + "\n !!! %s %s !!!"\
                 %(str(datetime.today()), str(e))
             self.logger.notifyChannel(self.LOG_NAME, netsvc.LOG_INFO, str(e))

class Currency_getter_factory():
    def register(self, class_name): 
        allowed = [
                          'Admin_ch_getter',
                          'PL_NBP_getter',
                          'ECB_getter',
                          'NYFB_getter',
                          'Google_getter',
                          'Yahoo_getter',
                          'bccr_getter' #Add BCCR
                    ]
        if class_name in allowed:
            class_def = eval(class_name)
            return class_def()
        else :
            raise UnknowClassError

#== Class to add CR rates  
class bccr_getter(Currency_getter_factory):
    
    log_info = " "
    
    #Parse url
    def get_url(self, url):
        """Return a string of a get url query"""
        try:
            import urllib
            objfile = urllib.urlopen(url)
            rawfile = objfile.read()
            objfile.close()
            return rawfile
        except ImportError:
            raise osv.except_osv('Error !', self.MOD_NAME+'Unable to import urllib !')
        except IOError:
            raise osv.except_osv('Error !', self.MOD_NAME+'Web Service does not exist !')
    
    def get_updated_currency(self, cr, uid, currency_array, main_currency):
        
        logger2 = logging.getLogger('bccr_getter')
        """implementation of abstract method of Curreny_getter_interface"""
        today = time.strftime('%d/%m/%Y')
        url1='http://indicadoreseconomicos.bccr.fi.cr/indicadoreseconomicos/WebServices/wsIndicadoresEconomicos.asmx/ObtenerIndicadoresEconomicos?tcNombre=clearcorp&tnSubNiveles=N&tcFechaFinal=' + today + '&tcFechaInicio='
        url2='&tcIndicador='

        from xml.dom.minidom import parseString
        self.updated_currency_sale = {} #separate sale from purchase. Two different webservices
        self.updated_currency_purchase = {}
        
        for curr in currency_array :
            self.updated_currency_sale[curr] = {}
            self.updated_currency_purchase [curr]= {}
            
            # Get the last rate for the selected currency
            currency_obj = pooler.get_pool(cr.dbname).get('res.currency')
            currency_rate_obj = pooler.get_pool(cr.dbname).get('res.currency.rate')            
            currency_id = currency_obj.search(cr, uid, [('name','=',curr)])            
            
            if not currency_id:
                continue            
            
            currency = currency_obj.browse(cr, uid, currency_id)[0] #only one currency
            last_rate_id = currency_rate_obj.search(cr, uid, [('currency_id','in',currency_id)], order='name DESC', limit=1)
            last_rate = currency_rate_obj.browse(cr, uid, last_rate_id)
            if len(last_rate):
                last_rate_date = last_rate[0].name
                last_rate_date = datetime.strptime(last_rate_date,"%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                last_rate_date = today

            url = url1 + last_rate_date + url2            
           
            #=======Get code for sale and purchase rate
            
            #1. Sale rate code 
            url_sale = url + currency.code_rate #sale rate for currency.               
            if url_sale:
                sale_list_rate = []
                logger2.info(url_sale)
                rawstring = self.get_url(url_sale)
                dom = parseString(rawstring)
                nodes = dom.getElementsByTagName('INGC011_CAT_INDICADORECONOMIC')
                for node in nodes:
                    num_valor = node.getElementsByTagName('NUM_VALOR')
                    if len(num_valor):
                        rate = num_valor[0].firstChild.data
                    else:
                        continue
                    des_fecha = node.getElementsByTagName('DES_FECHA')
                    if len(des_fecha):
                        date_str = des_fecha[0].firstChild.data.split('T')[0]
                    else:
                        continue
                    if float(rate) > 0:
                       self.updated_currency_sale[curr][date_str] = rate
                        
            #2. Purchase code rate
            if currency.second_rate:
                url_purchase = url + currency.second_code_rate #sale rate for currency. 
                if url_purchase:
                    purchase_list_rate = []
                    logger2.info(url_purchase)
                    rawstring = self.get_url(url_purchase)
                    dom = parseString(rawstring)
                    nodes = dom.getElementsByTagName('INGC011_CAT_INDICADORECONOMIC')
                    for node in nodes:
                        num_valor = node.getElementsByTagName('NUM_VALOR')
                        if len(num_valor):
                            rate = num_valor[0].firstChild.data
                        else:
                            continue
                        des_fecha = node.getElementsByTagName('DES_FECHA')
                        if len(des_fecha):
                            date_str = des_fecha[0].firstChild.data.split('T')[0]
                        else:
                            continue
                        if float(rate) > 0:
                            self.updated_currency_purchase[curr][date_str] = rate
                           
        logger2.info(self.updated_currency_sale) 
        return self.updated_currency_sale, self.updated_currency_purchase, self.log_info
