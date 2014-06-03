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

import pooler
import time
import math
from tools.translate import _
from openerp.addons.account_report_lib.account_report_base import accountReportbase

class Parser(accountReportbase):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'cr': cr,
            'uid': uid,
            'storage':{},
            'get_today': self.get_today,
            'display_inventory':self.display_inventory,  
            'get_products_order': self.get_products_order, 
            'set_total_result_by_product': self.set_total_result_by_product,           
        })
    
    #=========== SET AND GET DATA ==============================================
    def get_today(self):
        return time.strftime("%d/%m/%Y")
    
    def get_inventory(self, data):
        return self._get_form_param('inventory', data)
    
    def get_product_ids(self, data):
        return self._get_info(data,'product_ids', 'product.product')
  
    #set data to use in odt template. 
    def set_data_template(self, data):        
      
        #self.localcontext['storage'].update(dict_update)
        return False
    
    #============== DISPLAY DATA ===============================================    
    def display_inventory(self, data):
        inventory = self.get_inventory(data)
        if inventory == 'qty_available':
            return _('Quantity on Hand')
        elif inventory == 'virtual_available':
            return _('Forecasted Quantity')
        
    #===========================================================================
    
    """1. Build a domain with all search criteria (this is for products) """
    def build_search_criteria(self, data):
        list_tuples = []
        list_ids = []

        #******Products 
        product_ids = self.get_product_ids(data) #browse_record m2m
        if not product_ids:
            product_ids = self.pool.get('product.product').search(self.cr, self.uid, [])
            domain = ('id','in', product_ids)
        else:
            for product in self.get_product_ids(data):
                list_ids.append(product.id)
            domain = ('id','in', list_ids)
        list_tuples.append(domain)
        
        return list_tuples
    
    """2. Get products that match with domain """
    def get_products_order(self, data):
        
        #Search criteria
        domain = self.build_search_criteria(data)        
        #Find assets
        product_ids = self.pool.get('product.product').search(self.cr, self.uid, domain, order = 'name ASC')
        product_obj = self.pool.get('product.product').browse(self.cr, self.uid, product_ids)        
        #keep list in storage
        dict_update = {'products': product_obj,}        
        self.localcontext['storage'].update(dict_update)        
        return product_obj
        
    def set_total_result_by_product(self, data):
        totals = {'available_quantity':0.0, 'manu_quantity':0.0, 'total':0.0}
        products = {}
        value_list_lines = []
        value_list_mrp = []
        product_uom = self.pool.get('product.uom')
        
        #Extract value from wizard
        inventory = self.get_inventory(data)
        
        for product in self.get_products_order(data):
            products[product.id] = totals
            #Depends of inventory option
            if inventory == 'qty_available':
                quantity = product.qty_available
            elif inventory == 'virtual_available':
                quantity = product.virtual_available
            products[product.id]['available_quantity'] = quantity
            
            #The minimum quantity is the lower amount for mrp_bom.bom_lines
            mrp_bom_product_ids = self.pool.get('mrp.bom').search(self.cr, self.uid, [('product_id', '=', product.id)])
            for mrp_bom in self.pool.get('mrp.bom').browse(self.cr, self.uid, mrp_bom_product_ids):
                for line in mrp_bom.bom_lines:
                    #Depends of inventory option
                    if inventory == 'qty_available':
                        line_produc_quantity = line.product_id.qty_available
                    elif inventory == 'virtual_available':
                        line_product_quantity = line.product_id.virtual_available
                    
                    #comparison must be between product_id.uom_id in line and line.uom_id
                    if line.product_uom.id == line.product_id.product_tmpl_id.uom_id.id:
                        manu_quantity = line_produc_quantity / line.product_qty                         
                    else:
                        #conversion is from line.product_id.uom_id to line.uom_id
                        conver_quantity = product_uom._compute_qty(self.cr, self.uid, line.product_id.product_tmpl_id.uom_id.id, line_produc_quantity, line.product_uom.id)
                        manu_quantity = conver_quantity / line.product_qty
                    
                    value_list_lines.append(manu_quantity)
                
                #create a list with values for all lines, extract the minimum
                #value and keep this in another list.
                #review another (if exists) mrp.bom and repeat the process.
                #Finally extract the minimum value for mrp.bom list
                minimun_mrp = min(value_list_lines)
                value_list_mrp.append(minimun_mrp)
               
            #Get the minimum final value
            value_min_final = min(value_list_mrp)
            #Get final result
            products[product.id]['manu_quantity'] = math.floor(value_min_final) #floor round to lower value ex. 6.7 -> 6     
        
        products[product.id]['total'] = products[product.id]['available_quantity'] + products[product.id]['manu_quantity']                            
        
        dict_update = {'results': products,}        
        self.localcontext['storage'].update(dict_update)
        return False