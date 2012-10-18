from osv import fields,osv
from mx import DateTime
import netsvc
import tools
import pooler
import time
import datetime
import math
import os
import traceback
import traceback
from pprint import pprint
from pprint import PrettyPrinter

from tools.translate import _

class magento_stadistic (osv.osv):
    _name = 'magento.stadistic'
    _description = 'Magento stadistic info'
    _columns = {
        'product_ids': fields.many2one('product.product','Product'),
        'date_out_of_stock': fields.datetime('Date'),
        'customer_ids': fields.many2one('res.partner','Customer'),
        'qty_product':fields.integer('Quantity'),      
        'address':fields.related('customer_ids','address',type="one2many",relation="res.partner.address",string="Address",store=False)                 
    } 
    
    _defaults = {
        'date_out_of_stock': lambda *a: '2012-01-01',
        'qty_product': lambda*a: 1,
    }
    
    _sql_constraints = [
        (
            'qty_product_not_zero',
            'CHECK(qty_product > 0)',
            'The quantity of product must be greater than 0.'),
            ]

    def save_product (self,cr,uid,product_id,customer_id,qty_product,date_order):
        magento_connect = self.pool.get('sneldev.magento')

        #First check if the product don't exist in the stadistic
        list_stadistic = self.pool.get('magento.stadistic').search(cr, uid, 
                                                                   [('product_ids', '=', product_id),
                                                                    ('customer_ids','=',customer_id),
                                                                    ('date_out_of_stock','=',date_order)])
        if len(list_stadistic) == 0:                
            #Import the product. If exist, update the info
            result = magento_connect.import_products(cr, uid,product_id)
            
            if result == 0:
                #search the product in openerp and save in the magento_stadistic object
                product_ids = []
                product_ids_search = self.pool.get('product.product').search(cr, uid, [('magento_id', '=', product_id)])     
                product_ids_browse = self.pool.get('product.product').browse(cr, uid, product_ids_search)
                for product in product_ids_browse:
                    if product.id not in product_ids:
                        product_ids.append(product.id)
                
                #Search the customer, if exist, update info and        
                magento_connect.import_customers(cr,uid,customer_id)
                customer_ids = []
                customer_ids_search = self.pool.get('res.partner').search(cr,uid,[('magento_id','=',customer_id)])
                customer_ids_browse = self.pool.get('res.partner').browse(cr,uid,customer_ids_search)
                for customer in customer_ids_browse:
                    if customer.id not in customer_ids:
                        customer_ids.append(customer.id)
                
                indice = 0
                
                day = int(date_order[0:2])
                month = int(date_order[3:5])
                year = int(date_order[6:11])
                
                hour = int(date_order[11:13])
                minute = int(date_order[14:16])
                second = int(date_order[17:19])
                
                date_object = datetime.datetime(year,month,day,hour,minute,second)
                                                        
                for p in product_ids:                
                    product_of_stock = {
                        'product_ids':product_ids[indice],
                        'date_out_of_stock': date_object,
                        'customer_ids':customer_ids[0],
                        'qty_product':qty_product,
                    } 
                    indice + 1                 
                    self.pool.get('magento.stadistic').create(cr, uid, product_of_stock)
                return 0
                    
            else:
                raise osv.except_osv(_('Error !'), _('Cannot get product, check Magento web user config'))
                return -1
                    
        else:
            raise osv.except_osv(_('Error !'), _('Already exist the stadistic'))
            return -1
    
magento_stadistic()