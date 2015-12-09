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
import logging
from datetime import datetime, timedelta
from openerp.addons.currency_rate_update.currency_rate_update import bccr_getter
from openerp import pooler 

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

class resCurrencyrateInherit(orm.Model):
    _inherit = "res.currency.rate"
    _columns = {
          'value_second_rate': fields.float('Second Rate', digits=(12,6), help="The second rate of the currency of rate 1")
                }
    
class res_currency(osv.Model):
    _inherit = 'res.currency' 
    _columns = {
            'second_rate': fields.boolean('Have second rate'),
            'second_code_rate': fields.char('Second Code Rate', size=64),
            
    }
    
    def _get_current_rate(self, cr, uid, ids, raise_on_no_rate=True, context=None):
        if context is None:
            context = {}
        res = {}
        if 'second_rate' in context:
            second_rate = context['second_rate']
            if second_rate: 
                date = context.get('date') or time.strftime('%Y-%m-%d')
                for id in ids:
                    cr.execute('SELECT value_second_rate FROM res_currency_rate '
                               'WHERE currency_id = %s '
                                 'AND name <= %s '
                               'ORDER BY name desc LIMIT 1',
                               (id, date))
                    if cr.rowcount:
                        res[id] = cr.fetchone()[0]
                    elif not raise_on_no_rate:
                        res[id] = 0
                    else:
                        currency = self.browse(cr, uid, id, context=context)
                        raise osv.except_osv(_('Error!'),_("No currency rate associated for currency '%s' for the given period" % (currency.name)))
                return res
        return super(res_currency, self)._get_current_rate(cr, uid, ids, raise_on_no_rate=raise_on_no_rate, context=context) 
        
    def run_currency_update(self, cr, uid, arg1=None):
        rate_obj = self.pool.get('res.currency.rate')             
        #=======Currency to update
        #Find currency 
        currency = self.browse(cr, uid,[arg1],context=None)[0]

           #========Base currency
        res_currency_base_id = self.search(cr, uid, [('base', '=', True)])
        if not res_currency_base_id:
            raise Warning(_('There is no base currency set'))
        res_currency_base = self.browse(cr, uid, res_currency_base_id)[0]

        try:
            new_rate_ids = super(res_currency, self).run_currency_update(cr, uid, arg1=arg1)
            if currency.webservice == 'bccr_getter' and currency.second_rate:
                class_def = eval('bccr_getter_second_rate')
                getter = class_def()
                res, log_info = getter.get_updated_currency(cr, uid, [currency.name],res_currency_base.name)
                for date, value_second_rate in res[currency.name].iteritems():
                    rate_ids = rate_obj.search(cr, uid, [('currency_id','=',currency.id),('name','=',date)])
                    value_second_rate = float(value_second_rate)
                    if currency.sequence:
                        value_second_rate = 1.0/value_second_rate
                        vals = {'value_second_rate': value_second_rate}
                    else:
                        vals = {'value_second_rate': value_second_rate}
                    if len(rate_ids):
                        rate_obj.write(cr,uid, rate_ids, vals, context=None)
                        new_rate_ids += rate_ids
            self.logger2.info('Update finished...')
            return new_rate_ids
        except Exception as e:
            self.logger2.info("Unable to update %s, %s" % (currency.name, str(e)))


#== Class to add CR rates  
class bccr_getter_second_rate(bccr_getter):
      
    def get_updated_currency(self, cr, uid, currency_array, main_currency):
        
        logger2 = logging.getLogger('bccr_getter')
        """implementation of abstract method of Curreny_getter_interface"""
        today = time.strftime('%d/%m/%Y')
        url1='http://indicadoreseconomicos.bccr.fi.cr/indicadoreseconomicos/WebServices/wsIndicadoresEconomicos.asmx/ObtenerIndicadoresEconomicos?tcNombre=clearcorp&tnSubNiveles=N&tcFechaFinal=' + today + '&tcFechaInicio='
        url2='&tcIndicador='

        from xml.dom.minidom import parseString
        self.updated_currency = {} 

        
        for curr in currency_array :
            self.updated_currency[curr] = {}
            # Get the last rate for the selected currency
            currency_obj = pooler.get_pool(cr.dbname).get('res.currency')
            currency_rate_obj = pooler.get_pool(cr.dbname).get('res.currency.rate')
            currency_id = currency_obj.search(cr, uid, [('name','=',curr)])
            
            if not currency_id:
                continue
            
            currency = currency_obj.browse(cr, uid, currency_id)[0] #only one currency
            last_rate_id = currency_rate_obj.search(cr, uid, [('currency_id','in',currency_id)], order='name DESC', limit=1)
            last_rate = currency_rate_obj.browse(cr, uid, last_rate_id)
            #if len(last_rate):
             #   last_rate_date = last_rate[0].name
                #last_rate_date = datetime.strptime(last_rate_date,"%Y-%m-%d")
            #else:
            last_rate_date = today
            last_rate_datetime = time.strftime('%Y-%m-%d %H:%M:%S')
            url = url1 + last_rate_date + url2
           
            #=======Get code for rate
            url = url + currency.second_code_rate 
            list_rate = []
            logger2.info(url)
            rawstring = self.get_url(url)
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
                   self.updated_currency[curr][last_rate_datetime] = rate   
        logger2.info(self.updated_currency)
        return self.updated_currency, self.log_info
