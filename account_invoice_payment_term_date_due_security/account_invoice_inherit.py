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

from osv import orm, osv, fields
from tools.translate import _

class accountInvoiceinherit(orm.Model):
    
     _inherit = 'account.invoice'
     
     def _get_payment_term(self, cr, uid, ids, fields, arg, context=None):
        res = {}        
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.payment_term:
                res[invoice.id] = invoice.payment_term.id
        return res
    
     def _get_date_due(self, cr, uid, ids, fields, arg, context=None):
        res = {}        
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.date_due:
                res[invoice.id] = invoice.date_due
        return res

     _columns = {
        'payment_term_visible': fields.function(_get_payment_term, type='many2one', relation='account.payment.term', 
            store={'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['payment_term'], 10),}, string="Payment Term", readonly=True, states={'draft':[('readonly',False)]},),
        
        'date_due_visible': fields.function(_get_date_due, type='date', string='Due Date', 
            store={'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['date_due'], 11),}, readonly=True, states={'draft':[('readonly',False)]},
                help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. The payment term may compute several due dates, for example 50% now and 50% in one month, but if you want to force a due date, make sure that the payment term is not set on the invoice. If you keep the payment term and the due date empty, it means direct payment."),  
        }
     
     def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):        
        res = super(accountInvoiceinherit, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice=date_invoice, payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)
        
        if 'payment_term' in res['value'].keys():
            res['value'].update({'payment_term_visible': res['value']['payment_term']})
        
        if 'date_due' in res['value'].keys():
            res['value'].update({'date_due_visible': res['value']['date_due']})
                
        return res   
    
     def onchange_payment_term_visible(self, cr, uid, ids, payment_term_visible, date_invoice, date_due):
                 
         if payment_term_visible:
             #Call method to change date_due
             res = super(accountInvoiceinherit, self).onchange_payment_term_date_invoice(cr, uid, ids, payment_term_visible, date_invoice)
             res['value'].update({'payment_term':payment_term_visible})
             #This change is because another module changes only date_due and this method
             #change the default value. If date_due is already assigned, it is necessary 
             #keep previous value 
             if date_due:
                 if date_due == res['value']['date_due']:
                     res['value'].update({'date_due_visible': res['value']['date_due']})
             else:
                res['value'].update({'date_due_visible': res['value']['date_due']})
             
         return res
            
     