#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from datetime import datetime 
from openerp.osv import osv, fields
from openerp.tools.translate import _

class ResPartner(osv.Model):
    
    _inherit = "res.partner"
    
    def credit_available_order(self, cr, uid, id, payment_term_id, value, date=False,  context=None):
        if not date:
            date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        
        payment_term_obj = self.pool.get('account.payment.term')
        result =  payment_term_obj.compute(cr, uid, payment_term_id, value, date_ref=date, context=context)
        sum = 0.0
        # elem is a tuple of date, value
        # example ('2014-03-27', 200.65)
        for elem in result:
            if elem[0] != date:
                sum += elem[1]
                
        if sum == 0.0:
            return True
        else:
            partner = self.browse(cr, uid, id[0], context=context)
            if partner.credit + sum <= partner.credit_limit:
                return True
            else:
                return False
    
    def credit_available_invoice(self, cr, uid, id, payment_term_id, value, date=False,  context=None):
        if not date:
            date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        
        payment_term_obj = self.pool.get('account.payment.term')
        result =  payment_term_obj.compute(cr, uid, payment_term_id, value, date_ref=date, context=context)
        sum = 0.0
        # elem is a tuple of date, value
        # example ('2014-03-27', 200.65)
        for elem in result:
            if elem[0] != date:
                sum += elem[1]
                
        if sum == 0.0:
            return True
        else:
            partner = self.browse(cr, uid, id[0], context=context)
            if partner.credit - sum <= partner.credit_limit:
                return True
            else:
                return False
    
class SaleOrder(osv.Model):
    
    _inherit = 'sale.order'
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        sale_order = self.browse(cr, uid, ids[0], context=context)
        
        if sale_order.payment_term:
            if self.pool.get('res.users').has_group(cr, uid,
            'account_invoice_payment_term.group_account_payment_term_unlimited'):
                return super(SaleOrder,self).action_button_confirm(cr, uid, ids, context=context)
            
            if not sale_order.partner_id.credit_available_order(sale_order.payment_term.id,
            sale_order.amount_total, date=sale_order.date_order, context=context):
                raise osv.except_osv(_('Error'),_('Not enough credit is available to confirm the order.'))
        
        return super(SaleOrder,self).action_button_confirm(cr, uid, ids, context=context)
    
class AccountInvoice(osv.Model):
    
    _inherit = 'account.invoice'
    
    def invoice_validate(self, cr, uid, ids, context=None):
        invoice = self.browse(cr, uid, ids[0], context=context)
        if invoice.type == 'out_invoice':
            if self.pool.get('res.users').has_group(cr, uid,
            'account_invoice_payment_term.group_account_payment_term_unlimited'):
                return super(AccountInvoice,self).invoice_validate(cr, uid, ids, context=context)
            
            if invoice.payment_term:
                date = invoice.date_invoice or False
                
                if not invoice.partner_id.credit_available_invoice(invoice.payment_term.id,
                invoice.amount_total, date=date, context=context):
                    raise osv.except_osv(_('Error'),_('Not enough credit is available to confirm the invoice.'))
        
        return super(AccountInvoice,self).invoice_validate(cr, uid, ids, context=context)
    