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
from lxml import etree
from openerp.tools.translate import _

class accountVoucherinherit(orm.Model):
    _inherit = 'account.voucher'
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        if context is None: context = {}

        if view_type == 'form':
            if not view_id and context.get('invoice_type'):
                if context.get('invoice_type') in ('out_invoice', 'out_refund'):
                    result = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_form')
                else:
                    result = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_vendor_payment_form')
                result = result and result[1] or False
                view_id = result
            if not view_id and context.get('line_type'):
                if context.get('line_type') == 'customer':
                    result = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_form')
                else:
                    result = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_vendor_payment_form')
                result = result and result[1] or False
                view_id = result

        res = super(accountVoucherinherit, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])

        #In this section is when some differences between supplier and customer are established
        if context.get('type', 'sale') in ('purchase', 'payment'):
            #Separate client and suppliers
            nodes = doc.xpath("//field[@name='partner_id']")
            for node in nodes:
                node.set('context', "{'default_customer': 0, 'search_default_supplier': 1, 'default_supplier': 1}")
                if context.get('invoice_type','') in ('in_invoice', 'in_refund'):
                    node.set('string', _("Supplier"))
            
            #Separate the journal types
            nodes = doc.xpath("//field[@name='journal_id']")
            for node in nodes:
                #Add a domain when the view is from supplier. 
                node.set('domain', "[('payment_method_supplier','=', True)]")
                    
        res['arch'] = etree.tostring(doc)
        return res
    
    def _compute_exchange_rate(self, cr, uid, ids, field_names, args, context=None):
        res_user_obj = self.pool.get('res.users')
        currency_obj = self.pool.get('res.currency')
        exchange_rate = 0.0        
        
        res = {}
        #Company currency for logged user
        res_user = res_user_obj.browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id
        
        #Today's date
        now = time.strftime('%Y-%m-%d')
        
        for voucher in self.browse(cr, uid, ids, context=context):
            #Depends of sequence, set initial and final currency
            if company_currency.sequence < voucher.currency_id.sequence:
                initial_currency = company_currency
                final_currency = voucher.currency_id
            else:
                initial_currency = voucher.currency_id
                final_currency = company_currency
            
            #Get exchange, depends of order sets before
            exchange_rate = currency_obj.get_exchange_rate(cr, uid, initial_currency, final_currency, now, context=context)            
            res[voucher.id] = exchange_rate
        
        return res            
            
    _columns = {
                'voucher_payment_rate' : fields.function(_compute_exchange_rate, string='Exchange Rate Commercial', type='float',),
                'voucher_payment_rate_currency_id' : fields.related('company_id', 'currency_id', string='Company Currency', type='many2one', relation='res.currency',),
            }
                  
        