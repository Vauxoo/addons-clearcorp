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
from tools.translate import _
import time

from openerp.addons.account_report_lib.account_report_base import accountReportbase
from openerp.addons.product.report.product_pricelist import product_pricelist

class Parser(accountReportbase, product_pricelist):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.localcontext.update({
            'cr' : cr,
            'uid': uid,
            'storage': {},
            'get_pricelist': self.get_pricelist, 
            'display_currency_name': self.display_currency_name, 
            'display_today': self.display_today, 
            'get_qty_titles': self.get_qty_titles, 
            'set_data_template': self.set_data_template, 
            'get_price_list_by_category':self.get_price_list_by_category, 
            'get_product_image':self.get_product_image,
        })

    #======== SET AND GET DATA =========#
    def set_data_template(self, objects, data):
        
        list_titles = self._get_titles(data['form'])
        qty_titles = self.get_qty_titles(data)
        main_list = self.get_price_list_by_category(objects, data)
        
        dict_update = {'list_titles': list_titles, 
                       'list': main_list,
                       'qty_titles':qty_titles,}       
         
        self.localcontext['storage'].update(dict_update)
        return False
    
    def get_pricelist(self, data):
        return self._get_info(data,'price_list', 'product.pricelist')
        
    def get_qty_titles(self, data):
        return len(self._get_titles(data['form']))
    
    #Titles are defined by qty in wizard that are different of zero
    def get_qty_titles(self, data):
        qty = 0
        list_titles = self._get_titles(data['form'])
        
        #Title is a dictionary where its keys are the qty defined in wizard
        #different of zero
        for title in list_titles:
            qty = len(title.keys())
        return qty
    
    """
        This function is a "dummy" function. LibreOffice doesn't permit frames 
        with same name. To print a image in a aeroo report, it's necessary to
        create a frame and in the name, call function like this:
            image:asimage(get_product_image(product['id']))
        But, in the template we have five different case of titles, depending of
        how many quantities have been selected in wizard (1-5). So, for that reason,
        it exists five frames with the same name and it isn't allow in LibreOffice.
        
        So, create a method, where depends of quantity of titles, assign a key and 
        with this key extract the image in template:
            image:asimage(get_product_image(image_key[key])), where key is a number
        between 1 and 5.
    """
    def get_product_image(self, product_id, data):
        image_dict= {}
        qty = self.get_qty_titles(data)
        product_image =  self.pool.get('product.product').browse(self.cr, self.uid, product_id, context=None).image_medium
        image_dict[qty] = product_image
        return image_dict 
        
    #========DISPLAY DATA ==========#
    def display_currency_name(self, data):
        pricelist = self.get_pricelist(data)
        return pricelist.currency_id.name
    
    def display_today(self):
        return time.strftime('%Y-%m-%d')
    
    #=========================================================================#
    def get_price_list_by_category(self, objects, data):
        """
            The method _get_categories return a list of dictionary, where
            key 'name' is a category name and key 'products' is a list of 
            products
            
            for dict in list:
                for product in dict['products']:
                     .....            
        @param objects: Product or list of products selected from view
        @param data: Data dictionary, with all information from wizard  
        """
        return self._get_categories(objects, data['form'])
    