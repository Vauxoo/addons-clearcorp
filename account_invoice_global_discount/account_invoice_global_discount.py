# -*- encoding: utf-8 -*-
##############################################################################
#
#    account_invoice_global_discount.py
#    account_invoice_global_discount
#    First author: Carlos Vásquez <carlos.vasquez@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2010-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without modification, are
#    permitted provided that the following conditions are met:
#    
#       1. Redistributions of source code must retain the above copyright notice, this list of
#          conditions and the following disclaimer.
#    
#       2. Redistributions in binary form must reproduce the above copyright notice, this list
#          of conditions and the following disclaimer in the documentation and/or other materials
#          provided with the distribution.
#    
#    THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ``AS IS'' AND ANY EXPRESS OR IMPLIED
#    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#    
#    The views and conclusions contained in the software and documentation are those of the
#    authors and should not be interpreted as representing official policies, either expressed
#    or implied, of ClearCorp S.A..
#    
##############################################################################

from osv import osv,fields
from tools import config
import decimal_precision as dp

class account_invoice_line_ccorp(osv.osv):
    '''
    Inherits account.invoice.line de add global discount feature.
    '''
    _inherit = 'account.invoice.line'
    
    def _amount_line_no_discount(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            if line.invoice_id:
                res[line.id] = line.price_unit * line.quantity
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
            else:
                res[line.id] = line.price_unit * line.quantity
        return res

    def _amount_line_ccorp(self, cr, uid, ids, prop, unknow_none,unknow_dict):
        return self.pool.get('account.invoice.line')._amount_line(cr, uid, ids, prop, unknow_none,unknow_dict)
    
    _columns = {
        'price_subtotal': fields.function(_amount_line_ccorp, method=True, string='Subtotal (discounted)',store=True, type="float", digits_compute=dp.get_precision('Account')),
        'price_subtotal_not_discounted': fields.function(_amount_line_no_discount, method=True, string='Subtotal',store=True, type="float", digits_compute=dp.get_precision('Account')),
    }
account_invoice_line_ccorp()

class account_invoice_ccorp(osv.osv):
    '''
    Inherits account.invoice to add global discount feature.
    '''
    
    _inherit = 'account.invoice'

    def _amount_all_ccorp(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr,uid,ids, context=context):
            res[invoice.id] = {
                'invoice_discount': 0.0,
                'amount_discounted': 0.0,
                'amount_untaxed_not_discounted': 0.0,
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed_not_discounted'] += line.price_subtotal_not_discounted
                res[invoice.id]['amount_discounted'] += line.price_subtotal_not_discounted - line.price_subtotal
            if res[invoice.id]['amount_untaxed_not_discounted'] == 0:
                res[invoice.id]['invoice_discount'] = 0
            else:
                res[invoice.id]['invoice_discount'] = 100 * res[invoice.id]['amount_discounted'] / res[invoice.id]['amount_untaxed_not_discounted']
        return res
    
    def _get_invoice_line_ccorp(self, cr, uid, ids, context=None):
        return self.pool.get('account.invoice')._get_invoice_line(cr, uid, ids, context)

    def _get_invoice_tax_ccorp(self, cr, uid, ids, context=None):
        return self.pool.get('account.invoice')._get_invoice_tax(cr, uid, ids, context)
    
    _columns = {
        'invoice_discount': fields.function(_amount_all_ccorp, method=True, digits_compute=dp.get_precision('Account'), string='Discount (%)',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax_ccorp, None, 20),
                'account.invoice.line': (_get_invoice_line_ccorp, ['price_unit','invoice_line_tax_id','quantity','discount'], 20),
            },
            multi='ccorp'),
        'amount_discounted': fields.function(_amount_all_ccorp, method=True, digits_compute=dp.get_precision('Account'), string='Discount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax_ccorp, None, 20),
                'account.invoice.line': (_get_invoice_line_ccorp, ['price_unit','invoice_line_tax_id','quantity','discount'], 20),
            },
            multi='ccorp'),
        'amount_untaxed_not_discounted': fields.function(_amount_all_ccorp, method=True, digits_compute=dp.get_precision('Account'),string='Subtotal',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax_ccorp, None, 20),
                'account.invoice.line': (_get_invoice_line_ccorp, ['price_unit','invoice_line_tax_id','quantity','discount'], 20),
            },
            multi='ccorp'),
    }
account_invoice_ccorp()
