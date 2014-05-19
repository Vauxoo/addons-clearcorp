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
from report import report_sxw
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
            'display_user_name':self.display_user_name,
            'display_partner_name':self.display_partner_name, 
            'display_origin':self.display_origin,
            'display_type':self.display_type, 
            'set_data_template': self.set_data_template,
            'get_data_order':self.get_data_order,
            'display_name':self.display_name,
            'exist_lines_by_key':self.exist_lines_by_key, 
            'get_currency_name': self.get_currency_name, 
            'compute_price_total':self.compute_price_total, 
        })
    
    #=========== SET AND GET DATA ==============================================
    def get_type(self, data):
        return self._get_form_param('type', data)
    
    def get_origin(self, data):
        return self._get_form_param('origin', data)
    
    def get_currency_id(self, data):
        return self._get_info(data,'currency_id', 'res.currency')
    
    def get_user_id(self, data):
        return self._get_info(data,'user_id', 'res.users')
    
    def get_partner_id(self, data):
        return self._get_info(data,'partner_id', 'res.partner')
    
    def get_product_ids(self, data):
        return self._get_info(data,'product_ids', 'product.product')
    
    def get_category_ids(self, data):
        return self._get_info(data,'category_ids', 'product.category')
    
    def get_currency_name(self, currency_id):
        return self.pool.get('res.currency').browse(self.cr, self.uid, currency_id).name
    
    #Key could be a category or product
    def exist_lines_by_key(self, key):
        if key in self.localcontext['storage']['result'].keys():
            return True
        else:
            return False
    
    #set data to use in odt template. 
    def set_data_template(self, data):        
        result = self.classified_invoice_lines(data)        
        dict_update = {'result': result,}        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #============== DISPLAY DATA ===============================================
    def display_user_name(self, data):
        user = self.get_user_id(data)        
        if user:
            return user.name
        else:
            return _('No user')
    
    def display_partner_name(self, data):
        partner = self.get_partner_id(data)
        if partner:
            return partner.name
        else:
            return _('No partner')
    
    def display_origin(self, data):
        origin = self.get_origin(data)
        if origin == 'national':
            return _('National')
        elif origin == 'international':
            return _('International')
        elif origin=='mixed':
            return _('Mixed')
        else:
            return _('No origin')
    
    def display_type(self, data):
        type = self.get_type(data)
        if type == 'category':
            return _('Category')
        else:
            return _('Product')
    
    def display_name (self, key):
       if key == 'product':
           return _('Product: ')
       else:
           return _('Category: ')
        
    #===========================================================================
    
    """1. Build a domain with all search criteria (this is for account_invoice_lines) """
    def build_search_criteria(self, data):
        list_tuples = []
        category_ids = []
        product_ids = []
        
        #=================REQUIRED FIELDS==========================#
        #******Dates
        date_from = self.get_date_from(data)
        domain = ('invoice_id.date_invoice','>=', date_from)
        list_tuples.append(domain)
        
        date_to = self.get_date_to(data)
        domain = ('invoice_id.date_invoice','<=', date_to)
        list_tuples.append(domain)
        
        #===========================================================================
        # Origin:
        # For products = Create a on_change that change the domain in product_ids, this
        # domain depends of origin selected. If origin is False, get all products.
        #
        # For categories: Add filter for account.invoice.lines, where add categories ids and
        # all account.invoice.lines that have products with the origin selected.
        #===========================================================================
        #******Types (Category and Products)
        type = self.get_type(data)
        origin = self.get_origin(data)
        
        if type == 'category':
            category_list = self.get_category_ids(data) #browse_record m2m
            
            #if browse_record is False, get all categories
            if not category_list:
                category_ids = self.pool.get('product.category').search(self.cr, self.uid, [])
                domain = ('product_id.categ_id.id','in', category_ids)
            else:
                for category in category_list:
                    category_ids.append(category.id)
                domain = ('product_id.categ_id.id','in', category_ids)
            list_tuples.append(domain)
            #add origin filter
            if origin:
                domain = ('product_id.origin','=', origin)
                list_tuples.append(domain)
        
        elif type == 'product':
            product_list = self.get_product_ids(data) #browse_record m2m
             
            #If browse_record is false, get all products (This means that user doesn't select any product from wizard)
            if not product_list and origin:
                product_ids = self.pool.get('product.product').search(self.cr, self.uid, [('origin','=',origin)])
            elif not product_list and not origin:
                product_ids = self.pool.get('product.product').search(self.cr, self.uid, [])
                domain = ('product_id.id','in', product_ids)
                
            else:
                for product in product_list:
                    product_ids.append(product.id)            
                domain = ('product_id.id','in', product_ids)
            list_tuples.append(domain)
        
        #================NO REQUIRED FIELDS===========================#
        currency_id = self.get_currency_id(data) #browse_record m2o 
        if currency_id:
            domain = ('invoice_id.currency_id.id','in', [currency_id.id])
            list_tuples.append(domain)
        
        user_id = self.get_user_id(data)#browse_record m2o
        if user_id: 
            domain = ('invoice_id.user_id.id','in', [user_id.id])
            list_tuples.append(domain)
        
        partner_id = self.get_partner_id(data) #browse_record m2o
        if partner_id:
            domain = ('partner_id','in', [partner_id.id])
            list_tuples.append(domain)
        
        return list_tuples
    
    """2. Get account.invoice.lines that match with domain """
    def get_invoice_lines(self, data):
        
        #Search criteria
        domain = self.build_search_criteria(data)        
        #Find lines
        lines_ids = self.pool.get('account.invoice.line').search(self.cr, self.uid, domain, order = 'id ASC')
        lines_obj = self.pool.get('account.invoice.line').browse(self.cr, self.uid, lines_ids)
        
        return lines_obj
    
    """3. Classified invoice lines in 2 levels: Category or Product and currency """
    def classified_invoice_lines(self, data):
        res = {}
        #Get invoice lines
        invoice_lines = self.get_invoice_lines(data)
        type = self.get_type(data)
        
        for line in invoice_lines:
            #1. Classified by category or product
            if type == 'category':
                first_key = line.product_id.categ_id.id
            
            elif type == 'product':
                first_key = line.product_id.id
            
            if first_key not in res.keys():
                res[first_key] = {}
                
            #2. Classified by currency
            if line.invoice_id.currency_id.id not in res[first_key].keys():
                res[first_key][line.invoice_id.currency_id.id] = []
                
            res[first_key][line.invoice_id.currency_id.id].append(line)
        
        return res
    
    #Order alphabetically categories or products
    def get_data_order(self, data):
        order_list = []
        result = {}
        
        #Get type
        type = self.get_type(data)
        #Get origin
        origin = self.get_origin(data)
        
        if type == 'category':
            category_list = self.get_category_ids(data)
            if category_list:            
                for category in self.get_category_ids(data):
                    order_list.append(category.id)
                order_ids = self.pool.get('product.category').search(self.cr, self.uid, [('id','in',order_list)], order='name ASC')
            else:
                order_ids = self.pool.get('product.category').search(self.cr, self.uid, [], order='name ASC')
                
            order_obj = self.pool.get('product.category').browse(self.cr, self.uid, order_ids)
            result['category'] = order_obj
        else:
            product_list = self.get_product_ids(data)
            if product_list:
                for product in product_list:
                    order_list.append(product.id)
                order_ids = self.pool.get('product.product').search(self.cr, self.uid, [('id','in',order_list)], order='name ASC')
            
            else:
                #If browse_record is false, get all products (This means that user doesn't select any product from wizard)
                if not product_list and origin:
                    order_ids = self.pool.get('product.product').search(self.cr, self.uid, [('origin','=',origin)])
                elif not product_list and not origin:
                    order_ids = self.pool.get('product.product').search(self.cr, self.uid, [])
                
            order_obj = self.pool.get('product.product').browse(self.cr, self.uid, order_ids)
            result['product'] = order_obj
        
        dict_update = {'dict_order': result,}        
        self.localcontext['storage'].update(dict_update)
        return False
   
    def compute_price_total(self, line):
        return float(line.price_unit * line.quantity)
    