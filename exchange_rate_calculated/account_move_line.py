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

from osv import osv, fields, orm
import time
import copy

class accountMoveline(orm.Model):
    
    _inherit = 'account.move.line'
    
    """
        This method provides convert the amount_currency to debit or credit
        depends of currency selected. It only works in amount_currency to debit/credit.
        In debit/credit to amount_currency it isn't implemented.
    """
    def onchange_amount_currency(self, cr, uid, ids, date, amount_currency, currency_id, context=None):
        res_currency_obj = self.pool.get('res.currency')
        res_user_obj = self.pool.get('res.users')
        res = {'value':{}}
        if context is None:
            context = {}
        
        """
        1. Get currency for current company. 
        (The exchange rate for this case is from currency_company to currency_id)
        """
        res_user = res_user_obj.browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id
        
        """ 2. Get date as string"""
        if not date:
            date = time.strftime('%Y-%m-%d')
        copy_context = copy.copy(context)
        copy_context.update({'date':date})
            
        
        if amount_currency != 0 and currency_id:
            """3. Get amount_currency for today"""
            currency_selected = res_currency_obj.browse(cr, uid, currency_id, context=context)
            exchange_amount = res_currency_obj.get_exchange_rate(cr, uid, company_currency, currency_selected, date, context=copy_context)
            
            """4. Asign values to debit or credit """
            if amount_currency > 0:
                debit = amount_currency * exchange_amount
                dict = {'debit': debit, 'credit': 0.0}
            else:
                credit = -1 * amount_currency * exchange_amount #credit is positive
                dict = {'debit':0.0, 'credit':credit}
        
            res['value'] = dict
            
        return res
