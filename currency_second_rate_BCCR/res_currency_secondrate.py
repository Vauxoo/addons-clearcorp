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
    
    
    def _current_rate_computation(self, cr, uid, ids, name, arg, raise_on_no_rate, context=None):        
        
        if 'second_rate' in context:
            second_rate = context['second_rate']
            
            if second_rate:            
                if context is None:
                    context = {}
                res = {}
                if 'date' in context:
                    date = context['date']
                else:
                    date = time.strftime('%Y-%m-%d')
                date = date or time.strftime('%Y-%m-%d')
                # Convert False values to None ...
                currency_rate_type = context.get('currency_rate_type_id') or None
                # ... and use 'is NULL' instead of '= some-id'.
                operator = '=' if currency_rate_type else 'is'                    
                for id in ids:
                    cr.execute("SELECT currency_id, second_rate FROM res_currency_rate WHERE currency_id = %s AND name <= %s AND currency_rate_type_id " + operator +" %s ORDER BY name desc LIMIT 1" ,(id, date, currency_rate_type))                            
                    if cr.rowcount:
                        id, rate = cr.fetchall()[0]
                        res[id] = rate                
                    elif not raise_on_no_rate:
                        res[id] = 0
                    else:
                        raise osv.except_osv(_('Error!'),_("No currency rate associated for currency %d for the given period" % (id)))
            else:
                res = super(ResCurrency, self)._current_rate_computation(cr, uid, ids, name, arg, raise_on_no_rate, context)
        
        else:
            res = super(ResCurrency, self)._current_rate_computation(cr, uid, ids, name, arg, raise_on_no_rate, context)        
            
        return res
    
 