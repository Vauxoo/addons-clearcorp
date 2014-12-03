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

import copy
from openerp.osv import osv, fields
import time
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

class ResCurrency(osv.osv):
    _name = "res.currency"
    _inherit = "res.currency"
        
    _columns = {
        'sequence':fields.boolean('Rate Direction: '),
    }
    
    
    
    def _currency_priority(self, cr, uid, ids, ratedirection, arg1=None):
        curr_obj = self.pool.get('res.currency')
        rate_obj = self.pool.get('res.currency.rate')
       
        if ratedirection == True:
            currency_id = curr_obj.browse(cr, uid,ids,context=None)[0]
            rate_ids = rate_obj.search(cr, uid, [('currency_id','=',currency_id.id)])
            rates = rate_obj.browse(cr, uid,rate_ids,context=None)
            for rate in rates:
                 result = 1.0/float(rate.rate)
                 rate_obj.write(cr, uid,rate.id,{'rate':result} )
            
            
    
    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'sequence': None,
        })
        return super(ResCurrency, self).copy(cr, uid, id, default, context)
    
    def get_exchange_rate(self, cr, uid, res_currency_initial, res_currency_finally, name, context=None):
        """
        :param name: date of exchange rate
        """
        res_obj = self.pool.get('res.currency.rate')
        result = 0.00
        
        copy_context = copy.copy(context)
        copy_context.update({'date':name})
        
        res_currency_base_id = self.search(cr, uid, [('base', '=', True)])
        res_currency_base = self.browse(cr, uid, res_currency_base_id)[0]
        
        if res_currency_initial.id == res_currency_base.id:
            exchange_rate_dict = self.pool.get('res.currency')._current_rate(cr, uid, [res_currency_finally.id], name, arg=None, context=copy_context)
            result = exchange_rate_dict[res_currency_finally.id]
            
        elif res_currency_initial.id != res_currency_finally.id:
            currency_rate_initial = self.pool.get('res.currency')._current_rate(cr, uid, [res_currency_initial.id], name, arg=None, context=copy_context)[res_currency_initial.id]
            currency_rate_finally = self.pool.get('res.currency')._current_rate(cr, uid, [res_currency_finally.id], name, arg=None, context=copy_context)[res_currency_finally.id]
            result = currency_rate_initial * currency_rate_finally
        else:
            result = 1.00
            
        return result
