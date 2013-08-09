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

from osv import fields,osv
import decimal_precision as dp

class purchase_order_line(osv.osv):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'
    
    _columns = {
        'discount': fields.float('Discount (%)', digits=(16, 2)),        
    }
    
    _defaults = {
        'discount': lambda *a: 0.0,
        }
    
    _sql_constraints = [
        ('check_discount', 'CHECK (discount < 100)','The line discount must be leaser than 100 !'),
    ]
    
purchase_order_line()

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _description = 'Purchase Order'
    
    def action_invoice_create(self, cr, uid, ids, context=None):               
        
        """
        You have to make a super original method and 
        update invoice lines with the discount that lines has 
        on the purchase order. You can not directly update the discount 
        because the discount is calculated on the invoice
        """
        
        account_invoice_obj = self.pool.get('account.invoice')        
        account_invoice_line_obj = self.pool.get('account.invoice.line')
      
        res = super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)
        invoice_lines_ids = account_invoice_line_obj.search(cr,uid,[('invoice_id','=',res)],context=context)
        invoice_lines = account_invoice_line_obj.browse(cr,uid,invoice_lines_ids,context=context)
        
        for purchase in self.browse(cr, uid, ids, context=context):
            #zip is a function that enables iterating through two lists simultaneously.
            #for a,b in (list_a,list_b), where a is iterator for list_a and b is iterator for list_b
            #zip know if any of list is empty and stop the iteration
            
            #In this for, iterates in both list and extract the discount for purchase line
            #and update the invoice line with the id (invoice_line.id)
            for purchase_line,invoice_line in zip(purchase.order_line,invoice_lines):
                if purchase_line.discount is not None:
                    discount = purchase_line.discount  
                    account_invoice_line_obj.write(cr, uid,[invoice_line.id], {'discount': discount}, context=context)
        return res
    
    def _get_order_ccorp(self, cr, uid, ids, context=None):
        return self.pool.get('purchase.order')._get_order(cr, uid, ids, context)

    def _amount_all_ccorp(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_discount':0.0,
                'amount_subtotal_discount':0.0,
            }
            
            amount_untaxed_not_discount = por_disc = amount_discounted = amount_tax = total = 0.0 
            cur = order.pricelist_id.currency_id
            
            for line in order.order_line:
                #subtotal without discount and taxes
                amount_untaxed_not_discount += line.price_subtotal
                #----discount-------------#
                if line.discount > 0:
                   por_disc = line.discount / 100
                   amount_discounted += por_disc * line.price_subtotal
                #-----taxes---------------# 
                #taxes must be calculate with unit_price - discount
                price_unit_discount = line.price_unit - (line.price_unit * (line.discount / 100) )
                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, price_unit_discount, line.product_qty, line.product_id.id, order.partner_id)['taxes']:
                   amount_tax += c.get('amount', 0.0)
            
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, amount_untaxed_not_discount)
            res[order.id]['amount_discount']=cur_obj.round(cr, uid, cur, amount_discounted)
            res[order.id]['amount_subtotal_discount']=cur_obj.round(cr, uid, cur, (amount_untaxed_not_discount - amount_discounted))
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, amount_tax)
            res[order.id]['amount_total']=res[order.id]['amount_subtotal_discount'] + res[order.id]['amount_tax']
            
        return res

    _columns = {
        'amount_untaxed': fields.function(_amount_all_ccorp, digits_compute= dp.get_precision('Purchase Price'), string='Subtotal',
            store={
                'purchase.order.line': (_get_order_ccorp, None, 10),
            }, multi="sums", help="The amount without tax and discount"),
                
        'amount_tax': fields.function(_amount_all_ccorp, digits_compute= dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order.line': (_get_order_ccorp, None, 10),
            }, multi="sums", help="The tax amount"),
                
        'amount_total': fields.function(_amount_all_ccorp, digits_compute= dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order.line': (_get_order_ccorp, None, 10),
            }, multi="sums",help="The total amount"),
                
        'amount_discount': fields.function(_amount_all_ccorp, digits_compute= dp.get_precision('Sale Price'), string='Discount',
            store={
                'purchase.order.line': (_get_order_ccorp, None, 10),
            }, multi="sums",help="Amount discount"),   
        
        'amount_subtotal_discount': fields.function(_amount_all_ccorp, digits_compute= dp.get_precision('Sale Price'), string='Subtotal with discount',
            store={
                'purchase.order.line': (_get_order_ccorp, None, 10),
            }, multi="sums",help="Subtotal with discount"),   
    }
   
    
purchase_order()




    
