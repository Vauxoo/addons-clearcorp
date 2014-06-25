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

from osv import fields, orm
import time
from datetime import date, timedelta
from datetime import datetime
import copy

class accountInvoice(orm.Model):
    _inherit = 'account.invoice'    
        
    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False): 
        res = super(accountInvoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        res_date_payment = self.onchange_payment_term_date_invoice_partner(cr, uid, ids, res['value']['payment_term'], date_invoice, partner_id)
        
        #Update both dictionaries
        res['value'].update({'date_due': res_date_payment['value']['date_due'],})
        return res
    
    #Create a new function that receives a new parameter: partner_id  
    def onchange_payment_term_date_invoice_partner(self, cr, uid, ids, payment_term_id, date_invoice, partner_id):   
        
        #Call "old" function     
        res = super(accountInvoice, self).onchange_payment_term_date_invoice(cr, uid, ids, payment_term_id, date_invoice)
        
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id,context=None)
        payday_partner = int(partner.payday)
                
        if payday_partner:           
            date_due = datetime.strptime(res['value']['date_due'], "%Y-%m-%d")
            """See parameters for strftime function: http://www.tutorialspoint.com/python/time_strftime.htm"""
            day_due = int(date_due.strftime('%u')) #return weekday where Monday = 1

            #With both days, compute how many days exist between both days and 
            #recalculate new date due
            if day_due > int(payday_partner):
                days = 7 - day_due + int(datetime.today().strftime('%u'))
            else:
                days = int(payday_partner) - day_due
            
            new_date_due = date_due + timedelta(days=days)
            res['value'].update({'date_due': datetime.strftime(new_date_due,'%Y-%m-%d')})
        
        return res
            