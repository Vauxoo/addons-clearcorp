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
from datetime import datetime
import pooler
import time
from tools.translate import _
from openerp.addons.account_report_lib.account_report_base import accountReportbase

class Parser(accountReportbase):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.localcontext.update({
            'time': time,
            'cr' : cr,
            'uid': uid,
            'storage':{},
            'set_data_template':self.set_data_template,
            'opening_quantity':0.0,
            'final_cost':0.0,
            'final_quantity':0.0,
            'display_locations':self.display_locations, 
            'get_order_product':self.get_order_product,
            'is_product_dictionary':self.is_product_dictionary,
            'get_order_product': self.get_order_product,
            'get_name_product':self.get_name_product, 
            'get_location_name': self.get_location_name,
            'set_opening_quantity': self.set_opening_quantity,
            'return_opening_quantity': self.return_opening_quantity,
            'get_opening_cost': self.get_opening_cost, 
            'get_include_costs':self.get_include_costs,
            'get_data_stock_moves':self.get_data_stock_moves,
            'return_final_cost':self.return_final_cost, 
            'get_final_quantity':self.get_final_quantity,
        })
    
    #================== GET AND SET =======================#
    def get_name_product(self, product_id):
        product_product_obj = self.pool.get('product.product')
        product = product_product_obj.browse(self.cr, self.uid, product_id)
        name = product.name
        if product.code:
            name = product.code + ' - ' + product.name
        return name
    
    def get_location_name(self, location_id):
        return self.pool.get('stock.location').browse(self.cr, self.uid, location_id).complete_name   
    
    def get_product_ids(self, data):
        return self._get_info(data,'product_ids', 'product.product')
    
    def get_location_ids(self, data):
        return self._get_info(data,'location_ids', 'stock.location')
    
    def get_include_costs(self, data):
        return self._get_form_param('include_costs', data)
    
    def set_opening_quantity(self, data, product_id, location_id):
        date_from = self.get_date_from(data)
        opening_quantity = self.get_opening_quantity(self.cr, self.uid, data, product_id, location_id)
        self.localcontext['opening_quantity'] = opening_quantity 
        return opening_quantity    
    
    def return_opening_quantity(self):
        return self.localcontext['opening_quantity']
    
    def return_final_cost(self):
        return self.localcontext['final_cost']
    
    def get_final_quantity(self):
        return self.localcontext['final_quantity']
    
    def get_order_product(self, data):
        product_ids = []
        
        if not self.get_product_ids(data):
            product_ids = self.pool.get('product.product').search(self.cr, self.uid, [], order="code ASC")
            return self.pool.get('product.product').browse(self.cr, self.uid, product_ids)
        else:
           return self.get_product_ids(data) #browse record list
     
    def is_product_dictionary(self, product_id):
        if product_id in self.localcontext['storage']['result'].keys():
            return True
        else:
            return False
    
    def set_data_template(self, data):        
        result = self.get_dict_result(data)
        dict_update = {'result': result,}        
        self.localcontext['storage'].update(dict_update)
        return False
                   
    #=========================================================#
    
    #================ DISPLAY DATA ===========================#
    def display_locations(self, data):
       name = ''
       
       if not self.get_location_ids(data): #It means that non-one was selected
           return _('All locations')
       else:
           locations = self.get_location_ids(data)
           for location in locations:
               name += location.complete_name + ' , '
           return name       
    #===========================================================#
    
    """Build parameters. Extract information from wizard. """
    def built_parameters(self, data):
        product_ids = []
        location_ids = []
        
        date_from = self.get_date_from(data)
        date_to = self.get_date_to(data)
        include_costs = self.get_include_costs(data)
        
        #If user doesn't select any product, get all products
        x = self.get_product_ids(data)
        if not self.get_product_ids(data):
            product_ids = self.pool.get('product.product').search(self.cr, self.uid, [])
        else:
            for product in self.get_product_ids(data): 
                product_ids.append(product.id) 
        
        #If user doesnt's select any location, get all locations
        if not self.get_location_ids(data):
            location_ids = self.pool.get('stock.location').search(self.cr, self.uid, [])
        else:
            for location in self.get_location_ids(data): 
                location_ids.append(location.id)
        
        return date_from, date_to, include_costs, product_ids, location_ids
    
    """"
        Classified all stock_moves by product and location
    """     
    def get_dict_result(self, data):
        result = {}
        stock_move_obj = self.pool.get('stock.move')
       
        #parameters
        date_from, date_to, include_costs, product_ids, location_ids = self.built_parameters(data)
       
        #Get stock_move
        stock_move_ids = stock_move_obj.search(self.cr, self.uid, ['&', '&', '&', ('date','>=',date_from), ('date','<=',date_to), ('product_id', 'in', product_ids), '|',('location_id', 'in', location_ids), ('location_dest_id', 'in', location_ids)], order="date asc")
        stock_moves = stock_move_obj.browse(self.cr, self.uid, stock_move_ids)
        
        #Classified stock by product and location
        for stock in stock_moves:
            if stock.product_id.id not in result.keys():
                result[stock.product_id.id] = {}
            if stock.location_id.id not in result[stock.product_id.id].keys():
                result[stock.product_id.id][stock.location_id.id] = []
            result[stock.product_id.id][stock.location_id.id].append(stock)
            
        return result
    
    """Get data for a each stock_move. Keep this information in a dictionary,
       where id is stock_move id 
    """
    def get_data_stock_moves(self, opening_quantity, product_id, location_id, stock_move_list, data):
        stock_move_final = {}
        product_price_history_obj = self.pool.get('product.price.history')
        company_user_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id.id
        
        #Initialize final_quantity
        self.localcontext['final_quantity'] = opening_quantity
        
        for stock_move in stock_move_list:
            final_quantity = self.get_product_quantity(stock_move, location_id, opening_quantity)  
                               
            if self.get_include_costs(data):
                final_cost = self.get_opening_cost(data, product_id, opening_quantity)
            sign = 1   
            stock_move_dic = {'date': stock_move.date, 'type': stock_move.origin or '',}
            
            #Final Quantity 
            if stock_move.location_id.id == location_id:
                stock_move_dic.update ({'quantity_input': 0.00, 'quantity_output': stock_move.product_qty})
                self.localcontext['final_quantity'] -= stock_move.product_qty
                stock_move_dic.update({'final_quantity': self.localcontext['final_quantity']})
                sign = -1
            elif stock_move.location_dest_id.id == location_id:
                stock_move_dic.update ({'quantity_input': stock_move.product_qty, 'quantity_output': 0.00})
                self.localcontext['final_quantity'] += stock_move.product_qty
                stock_move_dic.update({'final_quantity': self.localcontext['final_quantity']})
                                  
            if self.get_include_costs(data):
                #Result of standard_price is a dictionary, where keys are product_id and value in field_names, in this case, 'standard_price'
                standard_price = product_price_history_obj._get_historic_price(self.cr, self.uid, [stock_move.product_id.id], company_user_id, datetime=stock_move.date, field_names=['standard_price'])
                if standard_price[stock_move.product_id.id]['standard_price'] == 0:
                    standard_price = self.pool.get('product.product').browse(self.cr, self.uid, stock_move.product_id.id).standard_price
                    total = stock_move.product_qty * standard_price
                else:
                    total = stock_move.product_qty * standard_price[stock_move.product_id.id]['standard_price']
                final_cost += total * sign
                #update final_cost
                self.localcontext['final_cost'] = final_cost                
                stock_move_dic.update ({'standard_price': standard_price, 'total': total, 'final_cost': final_cost})
             
            #Return a dictionary, where key is stock_move_id and all values related with that stock_move
            stock_move_final[stock_move.id] =  stock_move_dic
        
        dict_update={'stock_moves': stock_move_final}
        self.localcontext['storage'].update(dict_update)
        
    def get_opening_quantity(self, cr, uid, data, product_id, location_id):
        opening_quantity = 0.00
        stock_move_obj = self.pool.get('stock.move')
        
        date_from = self.get_date_from(data)
        stock_move_ids = stock_move_obj.search(cr, uid, ['&', '&', ('date','<',date_from), ('product_id', '=', product_id), '|',('location_id', '=', location_id), ('location_dest_id', '=', location_id)])
        stock_moves = stock_move_obj.browse(cr, uid, stock_move_ids)
        
        for stock_move in stock_moves:
            opening_quantity = self.get_product_quantity(stock_move, location_id, opening_quantity)
        return opening_quantity
       
    def get_opening_cost(self, data, product_id, opening_quantity):
        product_price_history_obj = self.pool.get('product.price.history')
        date_from = self.get_date_from(data)
        date= datetime.strptime(date_from, "%Y-%m-%d")
        company_user_id = self.pool.get('res.users').browse(self.cr, self.uid, self.uid).company_id.id           
        standard_price = product_price_history_obj._get_historic_price(self.cr, self.uid, [product_id], company_user_id, datetime=date, field_names=['standard_price'])                    
        opening_cost = standard_price[product_id]['standard_price'] * opening_quantity
        return opening_cost
        
    def get_product_quantity(self, stock_move, location_id, quantity):
        if stock_move.location_id.id == location_id:
            quantity = quantity - stock_move.product_qty
        elif stock_move.location_dest_id.id == location_id:
            quantity = quantity + stock_move.product_qty
        return quantity
