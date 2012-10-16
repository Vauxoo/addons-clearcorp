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
        'date_out_of_stock': fields.date('Date'),
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

    def save_product (self,cr,uid,product_id,customer_id,qty_product):
        magento_connect = self.pool.get('sneldev.magento')
        try:
            #First, import the product. If exist, update the info
            magento_connect.import_products(cr, uid,product_id)
            
            #search the product in openerp and save in the magento_stadistic object
            product_ids = []
            product_ids_openerp = self.pool.get('product.product').search(cr, uid, ['magento_id', '=', product_id])       
            for product in product_ids_openerp:
                if product.id not in product_ids:
                    product_ids.append(product.id)
            
            #Search the customer, if exist, update info and        
            magento_connect.import_customers(cr,uid,customer_id)
            customer_ids = []
            customer_ids_openerp = self.pool.get('res.partner').search(cr,uid,['magento_id','=',customer_id])
            for customer in customer_ids_openerp:
                if customer.id not in customer_ids:
                    customer_ids.append(customer.id)
            
            today = str(datetime.date.today())
            
            product_of_stock = {
                'product_ids':[(6, 0, product_ids )],
                'date_out_of_stock': today,
                'customer_ids':[(6, 0, customer_ids )],
                'qty_product':qty_product,
            } 
             
            self.pool.get('magento.stadistic').create(cr, uid, product_of_stock)
            
        except:
            #log.append('Cannot create stadistic')
            raise osv.except_osv(_('Error !'), _('Cannot get product, check Magento web user config'))
            #traceback.print_exc(file=sys.stdout)
            #log.print_traceback()  
            return -1
    
magento_stadistic()