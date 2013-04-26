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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
