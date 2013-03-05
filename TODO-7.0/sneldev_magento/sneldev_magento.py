#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 SnelDev (http://www.sneldev.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

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
from common_tools import *
import traceback
from pprint import pprint

from tools.translate import _

log = sneldev_log("magento_export.log");

class sneldev_magento(osv.osv):
    _name = 'sneldev.magento'
    _description = 'Magento website infos'
    _columns = {
        'name': fields.char('Name', size=128), 
        'url': fields.char('Magento base URL', size=128), 
        'api_user': fields.char('API User', size=64),
        'api_pwd': fields.char('API Password', size=64),
        'auto_export_stock': fields.boolean('Automatic stock export'),
        'auto_export_products': fields.boolean('Automatic products export'),
        'auto_import_products': fields.boolean('Automatic products import'),
        'auto_import_orders': fields.boolean('Automatic orders import'),
        'auto_import_credit_memos': fields.boolean('Automatic credit memos import'),
        'auto_script_path': fields.char('Syncronization Script Path', size=256),
        'sync_sleep': fields.integer('Time between synchronizations'),
        'sync_script_pid': fields.integer('PID of Sync Script'),
        'sync_status': fields.char('Syncronization status', size=128),
        'shipping_product': fields.many2one('product.product', 'Shipping Product', required=True, change_default=True),
        'default_category': fields.many2one('product.category', 'Default category for imported products', required=True, change_default=True),
        'magento_root_cat_id': fields.integer('Magento Root category ID'),
        'last_imported_product_timestamp': fields.char('Timestamp of latest imported product', size=128),
        'last_imported_category_timestamp': fields.char('Timestamp of latest imported category', size=128),
        'last_imported_invoice_timestamp': fields.char('Timestamp of latest imported invoice', size=128),
        'payment_journal': fields.many2one('account.journal', 'Payment Journal'),  
        'last_invoice_id': fields.integer('Last imported sale order'),
        'last_creditmemo_id': fields.integer('Last imported credit memo'),
        'auto_invoice_open': fields.boolean('Imported invoices automatically goes to Open state'),
        'auto_invoice_paid': fields.boolean('Imported invoices automatically goes to Paid state'),
        'inital_stock_location': fields.many2one('stock.location', 'Location for stock initialization'),
        'import_credit_memos': fields.boolean('Import credit memos after importing orders'),
        'last_imported_order_timestamp': fields.char('Timestamp of latest imported order', size=128),
        
    }
    
    _defaults = {
        'auto_export_stock': lambda *a: False,
        'auto_export_products': lambda *a: False,
        'auto_import_products': lambda *a: False,
        'auto_import_orders': lambda *a: False,
        'auto_import_credit_memos': lambda *a: False,
        'sync_sleep': lambda *a: 300,
        'sync_script_pid': lambda *a: -1,
        'last_creditmemo_id' : lambda *a: -1,
        'last_invoice_id': lambda *a: -1,
        'sync_status': lambda *a: 'Idle',
        'last_imported_invoice_timestamp': lambda *a: '2012-01-01',
        'last_imported_order_timestamp': lambda *a: '2012-01-01',
        'magento_root_cat_id': lambda *a: -1,
        'auto_invoice_open': lambda *a: False,
        'auto_invoice_paid': lambda *a: False,
    }
    
    def _unique(self, cr, uid, ids):
        res = self.pool.get('sneldev.magento').search(cr, uid,[])
        if len(res) > 1 :
            return False
        else :
            return True
    
    _constraints = [
        (_unique, 'Only one website supported at this time.', [])
    ]


    ##################################################################
    # Common functions
    ##################################################################  
    def get_magento_params(self, cr, uid):
        try:
            website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
            magento_params = self.pool.get('sneldev.magento').browse(cr, uid, [website_ids[0]])
            return magento_params
        except:
            log.append('Cannot find Magento shop')   
            raise osv.except_osv(_('Error !'), _('Cannot find Magento shop'))
        
    ##################################################################
    # Scheduler
    ##################################################################   
    def get_params(self, cr, uid):
        try:
            website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
            magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
            return {
                'sync_sleep': magento_params[0].sync_sleep, 
                'auto_export_stock': magento_params[0].auto_export_stock,
                'auto_export_products': magento_params[0].auto_export_products, 
                'auto_export_partners': magento_params[0].auto_export_partners,                 
                'auto_import_products': magento_params[0].auto_import_products, 
                'auto_import_orders': magento_params[0].auto_import_orders, 
                'auto_import_partners':magento_params[0].auto_import_partners,
                'auto_import_credit_memos': magento_params[0].auto_import_credit_memos,
                'sync_script_pid': magento_params[0].sync_script_pid,
            }
        except:
            return -1    
            
    def set_status(self, cr, uid, status):
        ids = self.pool.get('sneldev.magento').search(cr, uid, [])
        self.pool.get('sneldev.magento').write(cr, uid, ids[0], {'sync_status': str(status)})        
        return 0
        
    def set_pid(self, cr, uid, pid):
        ids = self.pool.get('sneldev.magento').search(cr, uid, [])
        self.pool.get('sneldev.magento').write(cr, uid, ids[0], {'sync_script_pid': pid})        
        return 0
                
    def sync_start(self, cr, uid):
        try:
            log.append('===== Sync start')
            website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
            magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
            if (magento_params[0].auto_script_path):
                pid = os.spawnl(os.P_NOWAIT, magento_params[0].auto_script_path)
            else:   
                log.append('Script not found in scheduler loop')  
                raise osv.except_osv(_('Error !'), _('Script not found in scheduler loop'))
        except:   
            log.append('Unknown error in scheduler loop')
            raise osv.except_osv(_('Error !'), _('Unknown error in scheduler loop'))
        return 0
        
    def sync_stop(self, cr, uid):
        log.append('===== Sync stop')
        ids = self.pool.get('sneldev.magento').search(cr, uid, [])
        self.pool.get('sneldev.magento').write(cr, uid, ids[0], {'sync_script_pid': -1})   
        
    ##################################################################
    # Categories export
    ##################################################################    
    def export_categories(self, cr, uid):
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        if (export_is_running() == False):
            try:
                log.append('===== Category export')
                website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
                magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
                [status, server, session] = magento_connect(self, cr, uid)
                if not status:
                    log.append('Cannot connect ' + str(server))   
                    set_export_finished()  
                    return -1
                cat_ids = self.pool.get('product.category').search(cr, uid, [('modified', '=', 'True'),('export_to_magento','=','True')])
                cats = self.pool.get('product.category').browse(cr, uid, cat_ids)
            except: 
                set_export_finished()  
                return -1 
                     
            for cat in cats:
                try:
                    log.append('Category: ' + cat.name)
                    if cat.magento_id == -1:
                        log.append('New')
                        category_data = {
                            'name': cat.name, 
                            'is_active': 1, 
                            'available_sort_by': 'name,price',
                            'default_sort_by': 'price', 
                            'include_in_menu': False,
                        }
                        log.append("Parent : " + str(cat.parent_id.magento_id))
                        magento_id = server.call(session, 'category.create', [1, category_data])
                        self.pool.get('product.category').write(cr, uid, cat.id, {'magento_id': magento_id, 'modified': False})
                        if cat.parent_id.magento_id and (cat.parent_id.magento_id != -1):
                            server.call(session, 'category.move', [magento_id, cat.parent_id.magento_id])
                        elif magento_params[0].magento_root_cat_id != -1:
                             server.call(session, 'category.move', [magento_id, magento_params[0].magento_root_cat_id])
                        log.append(magento_id)
                    else:
                        log.append('Old')  
                        log.append(cat.magento_id)  
                        category_data = {
                            'name': cat.name,  
                            'available_sort_by': 'name,price',
                        }
                        server.call(session, 'category.update', [cat.magento_id, category_data])
                        if cat.parent_id.magento_id and (cat.parent_id.magento_id != -1):
                            server.call(session, 'category.move', [cat.magento_id, cat.parent_id.magento_id])
                        self.pool.get('product.category').write(cr, uid, cat.id, {'modified': False})
                        log.append('Done')  
                except:
                    log.append('Error') 
                    log.print_traceback()   
                log.append('-----')   
            set_export_finished()
            return 0
        log.append('Export already running')
        raise osv.except_osv(_('Error !'), _('Export already running'))
        return -1
        

    ##################################################################
    # Products export
    ##################################################################
    def export_products(self, cr, uid,cat_ids_selected):
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        prod_ids = []
        
        if (export_is_running() == False):
            log.append('===== Product export')
            [status, server, session] = magento_connect(self, cr, uid)
            if not status:
                log.append('Cannot connect ' + str(server))   
                set_export_finished()  
                return -1  
                     
            # Ids are changed by those selected.
            # If cat_ids_selected is empty, the products that will be export are that modified and  have enabled export
            # If data is to be exported products matching the ids of the selected categories.
            if len(cat_ids_selected) == 0 :
                 prod_ids = self.pool.get('product.product').search(cr, uid, [('modified', '=', 'True'),('export_to_magento','=','True')])
            else:
                 for cat in cat_ids_selected:
                     prod_ids = self.pool.get('product.product').search(cr, uid, [('categ_id', '=', cat)])                 
                 
            prods = self.pool.get('product.product').browse(cr, uid, prod_ids)
            for prod in prods:
                try:
                    log.append('Product: ' + prod.name)
                    #if prod.code and prod.export_to_magento:
                    """It replaces the condition "export_to_magento" because in the first filter 
                    (if selected to export all categories) will bring all the products that are selected for export. 
                    If exported by categories associated products that match the selected category.
                    """
                    if prod.code: 
                        attribute_sets = server.call(session, 'product_attribute_set.list');
                        product_data = {
                            'status': True,
                            'name': prod.name,  
                            'sku': prod.code,
                        }
                        if prod.list_price:
                            product_data['price'] = str(prod.list_price) 
                        if prod.weight:    
                             product_data['weight'] = str(prod.weight)
                        if prod.magento_id == -1:
                            log.append('New')
                            magento_id = server.call(session, 'catalog_product.create', ['simple', attribute_sets[0]['set_id'], prod.code, product_data]);
                            self.pool.get('product.product').write(cr, uid, prod.id, {'magento_id': magento_id, 'modified': False})
                            log.append(magento_id)
                            if not prod.categ_id.magento_id == -1:
                                server.call(session, 'category.assignProduct', [prod.categ_id.magento_id, magento_id]);
                        else:
                            log.append('Old')
                            server.call(session, 'catalog_product.update', [prod.magento_id, product_data]);
                            self.pool.get('product.product').write(cr, uid, prod.id, {'modified': False})
                            log.append('Done')            
                    else:
                        log.append('Not set for export or no valid code')    
                        self.pool.get('product.product').write(cr, uid, prod.id, {'modified': False})
                except:
                    log.append('Error')  
                    log.print_traceback()
                log.append('-----')
            set_export_finished()
            return 0
        log.append('Export already running')
        raise osv.except_osv(_('Error !'), _('Export already running'))
        return -1

    ################################################################## 
    # Stock export
    ##################################################################
    def export_stock(self, cr, uid):
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        if (export_is_running() == False):
            log.append('===== Stock export')
            [status, server, session] = magento_connect(self, cr, uid)
            if not status:
                log.append('Cannot connect ' + str(server))   
                set_export_finished()  
                return -1  
            prod_ids = self.pool.get('product.product').search(cr, uid, [('magento_id', '!=', -1)])
            prods = self.pool.get('product.product').browse(cr, uid, prod_ids)
            
            sku_list = []
            for prod in prods:
                sku_list.append(prod.code)
            res = server.call(session, 'product_stock.list', [sku_list])
            magento_stock = {}
            for magento_prod in res:
                magento_stock[unicode(magento_prod['sku'])] = magento_prod['qty']
  
            for i in range(0, len(prod_ids)):
                try:
                    try:
                        if float(prods[i]['qty_magento']) != float(magento_stock[prods[i]['code']]):
                            entry = [prods[i]['code'], {'qty': prods[i]['qty_magento'], 'is_in_stock': 1}]
                            server.call(session,'product_stock.update', entry)
                            log.append(entry)
                            log.append('-----')
                    except:
                        log.append('Creating new stock entry')
                        entry = [prods[i]['code'], {'qty': prods[i]['qty_magento'], 'is_in_stock': 1}]
                        server.call(session,'product_stock.update', entry)
                        log.append(entry)
                        log.append('-----')
                except:
                    log.append('ERROR : ' + prods[i]['code'])
                    log.print_traceback()
                    log.append('-----')
                    raise osv.except_osv(_('Error !'), _('Error with product import'))
            set_export_finished()
            return 0 
       
        log.append('Export already running') 
        raise osv.except_osv(_('Error !'), _('Export already running'))  
    
        return -1

            
    ##################################################################
    # Update customer
    ##################################################################
    def update_customer(self, cr, uid, infos):
        try:
    		infos['customer_is_guest']
    	except:
    		infos['customer_is_guest'] = '0'
    
    	if infos['customer_is_guest'] == '1':
    		infos['customer_id'] = '0'
    		
        erp_customer = {  'magento_id' : infos['customer_id'],
                        'name' : infos['firstname'] + ' ' + infos['lastname'],
                        #'email'      : infos['email'],
                        'customer'   : True,
                        'supplier'   : False}
        
        log.append('\tUpdating customer ' + infos['firstname'] + ' ' + infos['lastname'])
        new_shipping_address = infos['shipping_address']
        new_billing_address = infos['billing_address']
        
    	# check to see if customer is guest, if so always create
    	if infos['customer_is_guest'] == '1':
    		cust_ids = []
    	else: 
    	    cust_ids = self.pool.get('res.partner').search(cr, uid, [('magento_id', '=', erp_customer['magento_id'])])
            
        if cust_ids == []:
            cust_ids = [self.pool.get('res.partner').create(cr, uid, erp_customer)]
            log.append("\t\tCustomer not found in OpenErp -> creation")
        else:
            self.pool.get('res.partner').write(cr, uid, [cust_ids[0]], erp_customer  )
            log.append("\t\tCustomer exists in OpenErp -> updating its info")
  
        if cust_ids == []:
            log.append("\t\tError! Customer not found and creation failed !!!")
            return [None , None, None]
   
        # Billing country
        try:
            new_billing_address_country = self.pool.get('res.country').name_search(cr, uid, new_billing_address['country_id'])[0][0]
        except:
            new_country = { 'name': new_billing_address['country_id'],
                            'code': new_billing_address['country_id']} 
            new_billing_address_country = self.pool.get('res.country').create(cr, uid, new_country)
  
        new_billing_address['street'] = new_billing_address['street'] + "\n "
        new_billing_address['street'] = new_billing_address['street'].split('\n')
        erp_contact_billing = { 'partner_id' : cust_ids[0],
                              'type' : 'invoice',
                              'name': new_billing_address['firstname'] + ' ' + new_billing_address['lastname'],
                              'street' : new_billing_address['street'][0],
                              'street2' : new_billing_address['street'][1],
                              'zip'    : new_billing_address['postcode'],
                              'city'   : new_billing_address['city'],
                              'country_id' : new_billing_address_country,
                              'phone' : new_billing_address['telephone']}
        # Shipping country
        try:
            new_shipping_address_country = self.pool.get('res.country').name_search(cr, uid, new_shipping_address['country_id'])[0][0]
        except:
            new_country = { 'name': new_shipping_address['country_id'],
                            'code': new_shipping_address['country_id']}
            new_shipping_address_country = self.pool.get('res.country').create(cr, uid, new_country)    
                                   
        new_shipping_address['street'] = new_shipping_address['street'] + "\n "
        new_shipping_address['street'] = new_shipping_address['street'].split('\n')
        erp_contact_shipping = {  'partner_id' : cust_ids[0],
                              'type' : 'delivery',
                              'name': new_shipping_address['firstname'] + ' ' + new_shipping_address['lastname'],
                              'street' : new_shipping_address['street'][0],
                              'street2' : new_shipping_address['street'][1],
                              'zip'    : new_shipping_address['postcode'],
                              'city'   : new_shipping_address['city'],
                              'country_id' : new_shipping_address_country,
                              'phone' : new_shipping_address['telephone']}
     
        contact_ids = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', cust_ids[0])])
        if (contact_ids != []):
            contacts = self.pool.get('res.partner.address').browse(cr, uid, contact_ids)
        else:
            contacts = []

        new_contact_ids = []
  
        for new_contact in [erp_contact_billing , erp_contact_shipping]:    
            if (new_contact == {}):
                continue      
            skip_contact_creation = False
            i = 0
            for _contact in contacts:
                is_contact_same = True
                contact={}
                #for key in ['first_name','last_name','street','street2','zip','country_id','city','phone']:
                for key in ['name','street','street2','zip','country_id','city','phone']:
                    if (key == 'country_id'):
                        if (_contact[key]['id'] != new_contact[key]):
                            is_contact_same = False
                            break
                    else:
                        if (_contact[key] != new_contact[key]):
                            is_contact_same = False
                            break

                if (is_contact_same == True):
                    skip_contact_creation = True
                    log.append("\t\tSkipping creation of " + new_contact['type'] + " contact address (already existing)")
                    break
          
                i = i + 1
      
            if (skip_contact_creation == False):
                log.append("\t\tCreation of new " + new_contact['type'] + " contact address")
                id_address = self.pool.get('res.partner.address').create(cr, uid, new_contact)
                new_contact_ids.append(id_address)
            else:
                new_contact_ids.append(contact_ids[i])
    
        return { 'id' : cust_ids[0] , 'billing_id' : new_contact_ids[0] , 'shipping_id' : new_contact_ids[1] }
    
    ##################################################################
    # Get Tax ID
    ##################################################################
    def get_tax_id(self, cr, uid, rate_percent): 
        rate = float(rate_percent) / 100
        int_rate = float(rate_percent) * 10
        low_rate = math.floor(int_rate + 0.5) / 1000
        high_rate = math.ceil(int_rate - 0.5) / 1000
        list_tax_ids = self.pool.get('account.tax').search(cr, uid, [('amount' , "<=", high_rate),('amount' , ">=", low_rate), ('type_tax_use', "=", 'sale')])
        if (list_tax_ids == []):
            # Need to add flag for TVA creation
            log.append('\t\t\tNo sale tax found with rate ' + str(rate) + '/' + str(low_rate) + '/' + str(high_rate))
            tax = {'name': ('Tax ' + str(rate*100) + '%'),
                            'amount': rate,
                            'type': 'percent',
                            'description': ('Magento' + str(rate*100) + '%'),
                            'price_include': False,
                            'type_tax_use': 'sale',
            }            
            tax_id = self.pool.get('account.tax').create(cr, uid, tax)
            log.append('\t\t\tCreated tax ' + str(tax_id))
        else:
            #should add a check in case of sevral taxes
            tax_id = list_tax_ids[0]
        return tax_id
            
    ##################################################################          
    # Categories import
    ##################################################################
    def _create_category(self, cr, uid, info_category, magento_params):
        category = { 'magento_id' : info_category['category_id'],
          'name' : info_category['name'],
          'modified' : False,
        }
        log.append('Updating category ' + info_category['category_id'] + ' ' + info_category['name'])
        if (info_category['level'] != '0'):
            if info_category['parent_id'] == str(magento_params[0].magento_root_cat_id):
                category['parent_id'] = False
                log.append("Parent is root")
            else:
                cat_ids = self.pool.get('product.category').search(cr, uid, [('magento_id', '=', info_category['parent_id'])])
                if cat_ids == []:
                    log.append("Parent not found")
                else:
                    category['parent_id'] = cat_ids[0]
                    log.append("Parent found " + str(cat_ids[0]))
        else:
            log.append("Root found " + str(category['magento_id']))
            self.pool.get('sneldev.magento').write(cr, uid, [magento_params[0].id], {'magento_root_cat_id':category['magento_id']})
            
        cat_ids = self.pool.get('product.category').search(cr, uid, [('magento_id', '=', category['magento_id'])])
        if cat_ids == []:
            cat_ids = [self.pool.get('product.category').create(cr, uid, category)]
            log.append("\tCategory not found in OpenErp -> creation")
        else:
            self.pool.get('product.category').write(cr, uid, [cat_ids[0]], category)
            log.append("\tCategory exists in OpenErp -> updating its info")
        if cat_ids == []:
            log.append("\tError! Category not found and creation failed !!!")
            return -1  
        log.append('-------------')
        for child in info_category['children']:
           self.pool.get('sneldev.magento')._create_category(cr, uid, child, magento_params) 
        return 0         
    
    def import_categories(self, cr, uid):
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        if (export_is_running() == False):
            try:
                log.append('===== Categories import')
                start_timestamp = str(DateTime.utc())
                website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
                magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
                # Get latest categories from Magento 
                self.pool = pooler.get_pool(cr.dbname) 
                [status, server, session] = magento_connect(self, cr, uid)
                if not status:
                    log.append('Cannot connect ' + str(server))   
                    set_export_finished()  
                    return -1 
                log.append('Logged in to Magento')
                info_category = server.call(session, 'category.tree',[])
                self.pool.get('sneldev.magento')._create_category(cr, uid, info_category, magento_params)
                self.pool.get('sneldev.magento').write(cr, uid, [website_ids[0]], {'last_imported_category_timestamp':start_timestamp})
            except:
                log.append('Cannot get categories, check Magento web user config')
                log.print_traceback()
                set_export_finished()
                return -1    
            set_export_finished()
            log.append('Import done')
            return 0
        log.append('Import already running')
        raise osv.except_osv(_('Error !'), _('Import already running'))     
        return -1    
        
    ##################################################################          
    # Product import
    ##################################################################
    def import_products(self, cr, uid,product_id):
        products = []
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        if (export_is_running() == False):
            try:
                log.append('===== Products import')
                start_timestamp = str(DateTime.utc())
                website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
                magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
                self.pool = pooler.get_pool(cr.dbname) 
                [status, server, session] = magento_connect(self, cr, uid)
                if not status:
                    log.append('Cannot connect ' + str(server))   
                    set_export_finished()  
                    return -1
                attribute_sets = server.call(session, 'product_attribute_set.list');
                log.append('Logged in to Magento')
            except:
                set_export_finished()
                raise osv.except_osv(_('Error !'), _('Connection error!!!'))       
                return -1
                
            increment = 300
            index = 1
            while True:
                if product_id != '':
                    new_product = server.call(session, 'product.info',[product_id])
                    products.append(new_product)
                    all_products = products
                else:
                    stop = index + increment - 1
                    log.append('Products ID from ' + str(index) + ' to ' + str(stop))
                    all_products = server.call(session, 'product.list',[{'product_id': {'from': str(index), 'to': str(stop)}}])
                    if last_import:
                        products = server.call(session, 'product.list',[{'updated_at': {'from': last_import}, 'product_id': {'from': str(index), 'to': str(stop)}}])
                        log.append('Last import: ' + last_import)
                    else:  
                        products = all_products
                    index = stop + 1
                
                for prod in products:
                    try:
                        log.append('Loading product ' + to_proper_uni(prod['sku']))
                        info_product = server.call(session, 'product.info',[prod['product_id']])
                        product = { 'magento_id' : info_product['product_id'],
                          'name' : info_product['name'],
                          'default_code' : info_product['sku'],
                          'modified' : False,
                          'export_to_magento': True,
                        }
                        try:
                            product['list_price'] = info_product['price']
                        except:
                            product['list_price'] = '0.00'
                        try:
                            product['weight'] = info_product['weight']
                        except:
                            product['weight'] = '0.00'
                        
                        
                        if info_product.has_key('category_ids'):
                            magento_cat_ids = info_product['category_ids']
                        elif info_product.has_key('categories'):
                            magento_cat_ids = info_product['categories']
                        else:
                            magento_cat_ids = []  
                        if magento_cat_ids:
                            cat_ids = self.pool.get('product.category').search(cr, uid, [('magento_id', '=', magento_cat_ids[0])])
                            if (cat_ids[0]):
                                product['categ_id'] = cat_ids[0]
                            else:
                                product['categ_id'] = magento_params[0].default_category.id    
                        else:
                            log.append('Default category')
                            product['categ_id'] = magento_params[0].default_category.id    
                       
                        log.append('Updating product ' + product['default_code'] + ' ' + product['name'])
                        prod_ids = self.pool.get('product.product').search(cr, uid, [('magento_id', '=', product['magento_id'])])
                        if prod_ids == []:
                            prod_ids = [self.pool.get('product.product').create(cr, uid, product)]
                            log.append("Product not found in OpenErp -> creation")
                        else:
                            self.pool.get('product.product').write(cr, uid, [prod_ids[0]], product)
                            log.append("Product exists in OpenErp -> updating its info")
    
                        if prod_ids == []:
                            log.append("Error! Product not found and creation failed !!!")
                            set_export_finished()
                            return -1 
                    except:
                        log.append("Error")
                        log.print_traceback()
                        raise osv.except_osv(_('Error !'), _('View log'))     
                        
                # If no products we can leave
                if (all_products == []):
                    self.pool.get('sneldev.magento').write(cr, uid, [website_ids[0]], {'last_imported_product_timestamp':start_timestamp})                                    
                    set_export_finished()
                    log.append("Done")
                    return 0
                else:                    
                    set_export_finished()
                    return 0
        else:          
            log.append('Import already running')
            raise osv.except_osv(_('Error !'), _('Import already running'))            
            return -1       
         
    ##################################################################          
    # Customer import
    ##################################################################
    
    def import_customers(self, cr, uid,customer_id):
        flag = False
        list = []
        customers = []
        magento_company = ''
                
        #if (export_is_running() == False):
        try:
            start_timestamp = str(DateTime.utc())
            website_ids = self.pool.get('sneldev.magento').search(cr, uid, [])
            magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
            self.pool = pooler.get_pool(cr.dbname) 
            [status, server, session] = magento_connect(self, cr, uid)
            if not status:
                log.append('Cannot connect ' + str(server))   
                set_export_finished()
                return -1
            log.append('Logged in to Magento')
        except:
            log.append('Cannot get customers, check Magento web user config')
            log.print_traceback()
            set_export_finished()
            raise osv.except_osv(_('Error !'), _('Cannot get customers, check Magento web user config'))      
            return -1 
        
        if customer_id != '':
            new_customer = server.call(session, 'customer.info',[customer_id])
            customers.append(new_customer)
        
        else:
            customers = server.call(session, 'customer.list')

        for cust in customers:
            try:
                """log.append('Loading customers ' + cust['customer_id'])"""
                info_cust = server.call(session, 'customer.info',[cust['customer_id']])
                
                ##### <<<<< check to see if customer is guest, if so always create >>>>> ######
                try:
                    info_cust['customer_is_guest']
                except:
                    info_cust['customer_is_guest'] = '0'
            
                if info_cust['customer_is_guest'] == '1':
                    info_cust['customer_id'] = '0'
            
                erp_customer = {
                    'magento_id' : int(info_cust['customer_id']),
                    'name' : info_cust['firstname'] + ' ' + info_cust['lastname'],
                    'email': str(info_cust['email']),
                    'customer'   : True,
                    'supplier'   : False,
                    'magento_company': '',
                }
                                    
                if info_cust['customer_is_guest'] == '1':
                    cust_ids = []
                else: 
                    #cust_ids = self.pool.get('res.partner').search(cr, uid, [('magento_id', '=', erp_customer['magento_id']),('email','=',str(info_cust['email']))])
                    cust_ids = self.pool.get('res.partner').search(cr,uid,[('email','=',info_cust['email'])])
                    
                if cust_ids == []:
                    cust_ids = [self.pool.get('res.partner').create(cr, uid, erp_customer)]
                    log.append("\t\tCustomer not found in OpenErp -> creation")
                else:
                    self.pool.get('res.partner').write(cr, uid, [cust_ids[0]], erp_customer  )
                    log.append("\t\tCustomer exists in OpenErp -> updating its info")
          
                if cust_ids == []:
                    log.append("\t\tError! Customer not found and creation failed !!!")
                    return [None , None, None]
                ####################################################################################################
                    
                info_address = server.call(session, 'customer_address.list', [cust['customer_id']])
                
                if (info_address != []):                               
                    ########## <<<<<<<CUSTOMERS ADDRESS>>>>>>> ##########################
                    list = []
                    try:
                        info_address = server.call(session, 'customer_address.list', [cust['customer_id']])
                        
                        for address in info_address:
                            
                            try:
                                new_address_country = self.pool.get('res.country').name_search(cr, uid, address['country_id'])[0][0]
                            except:
                                new_country = { 'name': address['country_id'],
                                        'code': address['country_id']}
                                address = self.pool.get('res.country').create(cr, uid, new_country)    

                            address['street'] = address['street'] + "\n "
                            address['street'] = address['street'].split('\n')
                            
                            #if the billing and shipping address are the same...
                            if address['is_default_shipping'] and address['is_default_billing']:
                                flag = True;
                                #BILLING
                                erp_contact_billing = {  'partner_id' : cust_ids[0],
                                      'type':'invoice',
                                      'name': address['firstname'] + ' ' + address['lastname'],
                                      'street' : address['street'][0],
                                      'street2' : address['street'][1],
                                      'zip'    : address['postcode'],
                                      'city'   : address['city'],
                                      'country_id' : new_address_country,
                                      'phone' : address['telephone'],
                                      'email': str(info_cust['email']),
                                      'magento_company': address['company']}

                                #SHIPPING
                                erp_contact_shipping = {  'partner_id' : cust_ids[0],
                                      'type':'delivery',
                                      'name': address['firstname'] + ' ' + address['lastname'],
                                      'street' : address['street'][0],
                                      'street2' : address['street'][1],
                                      'zip'    : address['postcode'],
                                      'city'   : address['city'],
                                      'country_id' : new_address_country,
                                      'phone' : address['telephone'],
                                      'email': str(info_cust['email']),
                                      'magento_company': address['company']}
                                
                                erp_customer['magento_company'] = address['company']
                                self.pool.get('res.partner').write(cr, uid, [cust_ids[0]], erp_customer  )
                                
                                list.append(erp_contact_billing)
                                list.append(erp_contact_shipping)
                                
                                
                                
                            #if the billing and shipping address are different ... 
                            else:
                                #Address type (Billing - Shipping)
                                if address['is_default_shipping']:
                                    type = 'delivery'
                                elif address['is_default_billing']:
                                    type ='invoice'
                                else:
                                    type = 'default'
                                                                                                
                                erp_contact = {  'partner_id' : cust_ids[0],
                                          #'type' : 'default',
                                          'type':type,
                                          'name': address['firstname'] + ' ' + address['lastname'],
                                          'street' : address['street'][0],
                                          'street2' : address['street'][1],
                                          'zip'    : address['postcode'],
                                          'city'   : address['city'],
                                          'country_id' : new_address_country,
                                          'phone' : address['telephone'],
                                          'email': str(info_cust['email']),
                                          'magento_company': address['company']}
                                
                                erp_customer['magento_company'] = address['company']
                                self.pool.get('res.partner').write(cr, uid, [cust_ids[0]], erp_customer  )
                                
                                list.append(erp_contact)                            
                                 
                            contact_ids = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', cust_ids[0])])
                            
                            if (contact_ids != []):
                                contacts = self.pool.get('res.partner.address').browse(cr, uid, contact_ids)
                            else:
                                contacts = []
    
                            new_contact_ids = []
                            is_contact_same = False
              
                            #for new_contact in [erp_contact]:
                            for new_contact in list:    
                                if (new_contact == {}):
                                    continue      
                                skip_contact_creation = False
                                i = 0
                                
                                for _contact in contacts:
                                    is_contact_same = True
                                    contact={}
                                    for key in ['name','street','street2','zip','country_id','city','phone']:
                                        if (key == 'country_id'):
                                            if (_contact[key]['id'] != new_contact[key]):
                                                is_contact_same = False
                                                break
                                        else:
                                            if (_contact[key] != new_contact[key]):
                                                is_contact_same = False
                                                break
                                            
                                    if (is_contact_same == True):
                                        skip_contact_creation = True
                                        log.append("\t\tSkipping creation of " + new_contact['type'] + " contact address (already existing)")
                                        break
                              
                                i = i + 1
                          
                                if (skip_contact_creation == False):
                                    log.append("\t\tCreation of new " + new_contact['type'] + " contact address")
                                    id_address = self.pool.get('res.partner.address').create(cr, uid, new_contact)
                                    new_contact_ids.append(id_address)
                                    
                                    if flag is False:
                                        list.remove(new_contact)
                                else:
                                    new_contact_ids.append(contact_ids[i])
                                
                    except:
                        log.append('Cannot get customers, check Magento web user config')
                        log.print_traceback()
                        set_export_finished()
                        raise osv.except_osv(_('Error !'), _('Cannot get customers, check Magento web user config'))  
                        return -1
                    
                else:
                    contact_ids = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', cust_ids[0])])
                    
                    if (contact_ids == []):
                       erp_contact = {  'partner_id' : cust_ids[0],
                            'type'       : 'other',
                            'name'       : info_cust['firstname'] + ' ' + info_cust['lastname'],
                            'street'     : None,
                            'street2'    : None,
                            'zip'        : None,
                            'city'       : None,
                            'country_id' : None,
                            'phone'      : None,
                            'email': str(info_cust['email']),
                            'magento_company': None}
                       
                       self.pool.get('res.partner.address').create(cr, uid, erp_contact)
                      
                       erp_customer['magento_company'] = None
                       self.pool.get('res.partner').write(cr, uid, [cust_ids[0]], erp_customer  )
                        
            except:
               log.append('Cannot get customers, check Magento web user config')
               log.print_traceback()
               set_export_finished() 
               raise osv.except_osv(_('Error !'), _('Cannot get customers, check Magento web user config'))                 

        if (customers == []):
            #self.pool.get('sneldev.magento').write(cr, uid, [website_ids[0]], {'last_imported_product_timestamp':start_timestamp})                                    
            set_export_finished()
            log.append("Done")
            return 0
        """
        else:
            log.append('Import already running') 
            raise osv.except_osv(_('Error'), _('Import already running')% ('error') )
            return -1                           
        """
    ##################################################################          
    # Initialize OpenERP stock 
    ##################################################################
    def init_stock(self, cr, uid):
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        if (export_is_running() == False):
            try:
                log.append('===== Stock init')
                [status, server, session] = magento_connect(self, cr, uid)
                if not status:
                    log.append('Cannot connect ' + str(server))   
                    set_export_finished()  
                    return -1  
                prod_ids = self.pool.get('product.product').search(cr, uid, [('magento_id', '!=', -1)])
                prods = self.pool.get('product.product').browse(cr, uid, prod_ids)
                
                sku_list = []
                for prod in prods:
                    sku_list.append(prod.code)
                res = server.call(session, 'product_stock.list', [sku_list])
                magento_stock = {}
                for magento_prod in res:
                    magento_stock[unicode(magento_prod['sku'])] = magento_prod['qty']
            except:
                log.append('Could not get stock from Magento')
                log.print_traceback()
                log.append('-----')  
                raise osv.except_osv(_('Error !'), _('Could not get stock from Magento'))  
            
            #try:
            magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
            location_id = magento_params[0].inital_stock_location.id
            inventry_obj = self.pool.get('stock.inventory')
            inventry_line_obj = self.pool.get('stock.inventory.line')
            name = 'Initial Magento Inventory'
            inventory_id = inventry_obj.create(cr , uid, {'name': name})
            log.append('New inventory ' + str(inventory_id) + ' / Location id : ' + str(location_id))
            for prod in prods:
                try:
                    log.append('\tAdding line : ' + prod['code'] + ' / ' + magento_stock[prod.code])
                    line_data ={
                        'inventory_id' : inventory_id,
                        'product_qty' : magento_stock[prod.code],
                        'location_id' : location_id,
                        'product_id' : prod.id,
                        'product_uom' : prod.uom_id.id,
                    }
                    inventry_line_obj.create(cr , uid, line_data)
                except:
                    log.append('\tSkipping : ' + prod['code'])
                    log.print_traceback()
                
                inventry_obj.action_confirm(cr, uid, [inventory_id])
                inventry_obj.action_done(cr, uid, [inventory_id])
            #except:
                #log.append('ERROR')
                #log.print_traceback()
                #log.append('-----')
                #raise osv.except_osv(_('Error !'), _('Error, check log files'))                    
            set_export_finished()
            return 0 
        
        else:
            log.append('Export already running') 
            raise osv.except_osv(_('Error !'), _('Export already running'))  
            return -1    
      
    ##################################################################          
    # Orders import
    ##################################################################
    def import_orders(self, cr, uid,entity_id,increment_id):
        list_orders = []
        
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        wf_service = netsvc.LocalService('workflow')
        if (export_is_running() == False):
            failed_order = False
            try:
                log.append('===== Orders import')
                ids = self.pool.get('sneldev.magento').search(cr, uid, [])
                magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
                
                self.pool = pooler.get_pool(cr.dbname) 
                [status, server, session] = magento_connect(self, cr, uid)
                if not status:
                    log.append('Cannot connect ' + str(server))   
                    set_export_finished()  
                    return -1
                
                #If the list is empty imports all the orders that have a date greater than the last import.
                #If the list contains an ID, it means that the module is magento and must import just 
                #the order that corresponds to the code that comes as parameter.
                
                if entity_id == '' and increment_id == '':
                    # Get latest sales orders in Magento 
                    list_orders = server.call(session,'sales_order.list',[{'updated_at': {'from': magento_params[0].last_imported_order_timestamp}}])
                else:
                    try:
                        new_order = info_order = server.call(session, 'sales_order.info',entity_id)                                                         
                        list_orders.append(new_order)
                    except:
                        new_order = info_order = server.call(session, 'sales_order.info',increment_id)                                                         
                        list_orders.append(new_order)
                    
                for order in list_orders:          
                    try:
                        info_order = server.call(session, 'sales_order.info',[order['increment_id']])
                        
                        name_sales_order = str(info_order['increment_id'])
                        
                        id_orders = self.pool.get('sale.order').search(cr, uid, [('magento_id', '=', info_order['order_id'])])
                        if (id_orders != []):
                            log.append("\tSales order " + name_sales_order + " already exists in ERP. Skipping")
                            continue
                        
                        log.append("\tGetting Info customer " + str(info_order['customer_id']))
                        try:
                            info_customer = server.call(session, 'customer.info' , [info_order['customer_id'] ])
                        except:
                            log.append("\t\tCustomer is guest")
                            info_customer = {
                                    'customer_id' : '0'
                                }
                    except:
                        log.append("\tERROR ! Invoice Skipped")
                        log.print_traceback()
                        failed_order = True
                        continue
            
                    try:                       
                        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid,[])
  
                        if (info_order['customer_is_guest'] == '1'):
                            info_customer['store_id'] = info_order['store_id']
                            info_customer['website_id'] = '1'
                            info_customer['email'] = info_order['customer_email']
                            info_customer['firstname'] = info_order['billing_address']['firstname']
                            info_customer['lastname'] = info_order['billing_address']['lastname']
                            info_customer['customer_is_guest'] = '1'
                            
                        info_customer['shipping_address'] = info_order['shipping_address']
                        info_customer['billing_address'] = info_order['billing_address']
                        erp_customer_info = self.pool.get('sneldev.magento').update_customer(cr, uid, info_customer)  

                        try:
                            #comments = u"Infos paiement\n"
                            comments = ""
                            for comment in info_order['status_history']:
                                if comment.has_key('comment') and len(comment['comment']) > 0:
                                    comments = comments + comment['comment'] + u"\n"
                            #Adding customer note
                            if (info_order.has_key("giftMessage")):
                                #comments = comments + u"Infos commande\n"
                                comments = comments + info_order["giftMessage"] + u"\n"
                        except:
                            pass
                            
                        # Creating sales order
                        erp_sales_order = { 'name' : name_sales_order,
                                            'order_policy' : 'manual',  
                                            #'client_order_ref' : name_invoice,
                                            #'client_order_ref' :name_sales_order,
                                            'state' : 'draft',  
                                            'partner_id' : erp_customer_info['id'],
                                            'partner_invoice_id'  : erp_customer_info['billing_id'],
                                            'partner_order_id'    : erp_customer_info['billing_id'],
                                            'partner_shipping_id' : erp_customer_info['shipping_id'],
                                            'pricelist_id'        : pricelist_ids[0],
                                            'magento_id'      : info_order['order_id'],
                                            'date_order'        : info_order['created_at'][:10],
                                            'note'      : comments
                        }
                        log.append("\tCreation of sales order in OpenErp " + name_sales_order)
                        id_order = self.pool.get('sale.order').create(cr, uid, erp_sales_order)
                        
                        # Sale order lines
                        #If products are not in openerp not listed in the detail of the bill. Must be found to be detailed on the invoice
                        missing_products_in_openerp = False
                        parents = {}
                        for item in info_order['items']:
                            if item.has_key('product_type') and (item['product_type'] == 'configurable'):
                                parents[item['item_id']] = {
                                    'base_price':   item['base_price'],
                                    'tax_percent':  item['tax_percent'],
                                }
                                log.append("\t\tParent product "  + str(item['sku']))
                                continue
                            if item.has_key('parent_item_id'):
                                try:
                                    item['base_price'] = str(float(item['base_price']) + float(parents[item['parent_item_id']]['base_price']))
                                    item['tax_percent'] = parents[item['parent_item_id']]['tax_percent']
                                except:
                                    log.append("\t\tNo parent price")
                            product_ids = self.pool.get('product.product').search(cr, uid, [('magento_id', '=', item['product_id'])])
                            if (product_ids == []):
                                log.append("\t\tProduct with magento_id " + str(item['product_id'])  + " not found in ERP - skipping")
                                missing_products_in_openerp = True
                                continue
                            product_id = product_ids[0]
                            my_product = self.pool.get('product.product').browse(cr, uid, product_id)     
                            log.append("\t\tCreation of sale order line for qty " + str(item['qty_ordered']) + " product " + my_product['name'])
                            try:
                                if (item['tax_percent'] != '0.0000'):
                                    tax_id = self.pool.get('sneldev.magento').get_tax_id(cr, uid, item['tax_percent'])
                                    if (tax_id == 0):
                                        raise 
                                    else:
                                        tax_ids = [[6,0,[tax_id]]]   
                                else:
                                    tax_ids = []
                                    log.append("\t\t\tNo tax " + item['tax_percent'])      
                            except:
                                log.append("\t\t\tError Found unsupported tax rate - skipping tax")
                                tax_ids = []      

                            erp_sales_order_line = {'order_id'        : id_order,
                                                  'product_id'      : product_id,
                                                  'name'            : my_product['name'],
                                                  'tax_id'          : tax_ids,
                                                  'price_unit'      : item['base_price'],
                                                  'product_uom'     : my_product['uom_id']['id'],
                                                  'product_uom_qty' : item['qty_ordered']
                            } 
                            id_order_line = self.pool.get('sale.order.line').create(cr, uid, erp_sales_order_line)
        
                        #Shipping costs
                        log.append("\t\tCreating shipping costs :" + str(info_order['shipping_amount']))
                        try:
                            my_shipping = magento_params[0].shipping_product
                            try:
                                if (info_order['shipping_tax_amount'] != '0.0000'):
                                    tax_percent = 100 * float(info_order['shipping_tax_amount']) / float(info_order['shipping_amount'])
                                    tax_id = self.pool.get('sneldev.magento').get_tax_id(cr, uid, tax_percent)
                                    if (tax_id == 0):
                                        raise  
                                    else:
                                        log.append("\t\t\tTax added, id: " + str(tax_id))
                                        tax_ids = [[6,0,[tax_id]]]      
                                else:
                                    tax_ids = []     
                            except:
                                tax_ids = []
                                log.append("\t\t\tError Found unsupported tax rate - skipping tax") 
                                 
                            erp_shipping_line = {
                                'order_id' : id_order,
                                'name': my_shipping['name'],
                                'product_id' : my_shipping['id'],
                                'price_unit':info_order['shipping_amount'],
                                'product_uom': my_shipping['uom_id']['id'],
                                'product_uom_qty' : 1,
                                'tax_id'          : tax_ids
                            }
                            id_order_line = self.pool.get('sale.order.line').create(cr, uid, erp_shipping_line)   
                        except:
                            log.append("\t\t\tNo Shipping costs")  
                            pass
                                
                        if missing_products_in_openerp:
                            log.append("\tMissing products in openERP, leaving in order in draft state")   
                            failed_order = True
                            continue                          
                            
                        log.append("\tConfirming Sales Order (Draft -> In progress)" )
                        wf_service.trg_validate(uid, 'sale.order', id_order, 'order_confirm', cr)
                              
                        # Creation of invoice
                        try:
                            log.append("\tCreating Invoice")  
                            self.pool.get('sale.order').manual_invoice(cr, uid, [id_order])
                            erp_invoice_id  = self.pool.get('sale.order').browse(cr, uid, id_order).invoice_ids[0]['id']
                            log.append("\t\tInvoice created : " + str(erp_invoice_id))
                            self.pool.get('account.invoice').write(cr,uid,[erp_invoice_id],{ "date_invoice" : invoice['created_at'][:10]})
                            
                            #Promo Code
                            erp_invoice_lines = self.pool.get('account.invoice').browse(cr, uid, erp_invoice_id).invoice_line
                            for erp_item in erp_invoice_lines:
                                erp_product_id = erp_item.product_id['id']
                                erp_product_magento_id = erp_item.product_id['magento_id']
                            
                                for item in info_order['items']:
                                    if (str(item["product_id"])==str(erp_product_magento_id)):
                                        if (item.has_key('discount_percent') and item["discount_percent"] != '0.0000'):
                                            log.append('\t\tAppending Discount to line with product magento id '+str(erp_product_magento_id))
                                            self.pool.get('account.invoice.line').write(cr,uid,[erp_item["id"]],{ "discount" : item["discount_percent"]})
                                        elif (item.has_key('discount_invoiced') and item['discount_invoiced']!='0.0000'):                
                                            #Managing fixed coupon reduction as a percentage also
                                            if (item.has_key('row_invoiced') and item['row_invoiced']!='0.0000'):
                                                discount = float(item['discount_invoiced'])
                                                total_price = float(item['row_invoiced'])                    
                                                discount_percent = discount / total_price * 100.0
                                                log.append('\t\tAppending Discount '+str(discount_percent)+' to line with product magento id '+str(erp_product_magento_id))
                                                self.pool.get('account.invoice.line').write(cr,uid,[erp_item["id"]],{ "discount" : discount_percent})
                                            else:
                                                log.append("Unsupported Promo Code type!")
                            #END MANAGEMENT PROMO CODE
                            
                            #Update Tax Base after promo codes
                            self.pool.get('account.invoice').button_reset_taxes(cr,uid,[erp_invoice_id])
                            
                            journal_code = info_order['payment']['method']
                            log.append("\t\tPayment method " + journal_code) 
                            #invoice_from_draft_to_paid(self, cr,uid, erp_invoice_id, info_invoice['created_at'] , name_invoice, journal_code ,context)
                                                
                        except:
                            log.append("\t\tError: Unable to create invoice")
                            log.print_traceback()
                            continue
                        
                        # Invoice from Draft to Open  
                        try:    
                            if magento_params[0].auto_invoice_open:    
                                log.append("\tConfirming Invoice (Draft -> Open)")
                                wf_service.trg_validate(uid, 'account.invoice', erp_invoice_id, 'invoice_open', cr)
                            else:
                                log.append("\tInvoice left in Draft")
                        except:
                            log.append("\tError: Unable to move invoice to Open status")
                            traceback.print_exc(file=sys.stdout)
                            continue
                            
                        # Invoice from Open to Paid   
                        try:
                            if magento_params[0].auto_invoice_paid and magento_params[0].auto_invoice_open:  
                                if magento_params[0].payment_journal:
                                    journal = magento_params[0].payment_journal
                                    log.append("\tPaying Invoice (Open -> Paid)")
                                else:
                                    log.append("\tNo journal set - Skipping invoice payment")
                                    continue
                                    
                                #from wizard_pay_invoice.py
                                log.append("\tGetting account period")
                                ids = self.pool.get('account.period').find(cr, uid, None)
                                period_id = False
                                if len(ids):
                                    period_id = ids[0]
                                else:
                                    log.append("\t\tNO ACCOUNT PERIOD AVAILABLE - SKIP invoice payment")
                                    raise
                                  
                                invoice = self.pool.get('account.invoice').browse(cr, uid, erp_invoice_id)
                                
                                # Need to change partner
                                log.append("\tMake customer reconcilable")
                                data = {'reconcile': True}
                                self.pool.get('account.account').write(cr, uid, [invoice.partner_id.property_account_receivable.id], data)
                  
                                amount = invoice.amount_total
                                ecriture_name = 'Order payment'
                                
                                writeoff_account_id = False
                                writeoff_journal_id = False
                                context={'date_p': info_invoice['created_at'], 'comment':''}
                                acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
                                if acc_id == []:
                                    log.append("\t\tERROR The journal does not have default credit - debit account")
                                else:
                                    self.pool.get('account.invoice').pay_and_reconcile(cr,uid,[erp_invoice_id], amount, acc_id, period_id, journal.id, writeoff_account_id, period_id, writeoff_journal_id, context, ecriture_name)
                                    log.append("\t\tPayment done")      
                            else:
                                log.append("\tInvoice not moved to Paid state")                                              
                        except:
                            pass
                            
                    except:
                        log.append("Invoice/Order skipped")  
                        failed_order = True 
                        log.print_traceback()
                if not failed_order:
                    today = str(datetime.date.today())
                    log.append("Update last import : " + today)
                    self.pool.get('sneldev.magento').write(cr, uid, [magento_params[0].id], {'last_imported_order_timestamp':today})
#                    log.append("Last invoice_id " + str(new_last_invoice_id))
#                    self.pool.get('sneldev.magento').write(cr, uid, [magento_params[0].id], {'last_invoice_id':new_last_invoice_id})
                set_export_finished()
                log.append("Done")
                return 0     
            except:
                log.append('Cannot import orders')
                traceback.print_exc(file=sys.stdout)
                set_export_finished()  
                return -1
        log.append('Import already running') 
        return -1       
        
    def _invoice_from_draft_to_paid(self, cr, uid, erp_invoice_id,invoice_created_at, name_invoice, journal_code):
        log.append("Invoice from draft to Open")
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', erp_invoice_id, 'invoice_open', cr)
        
        # Invoice from Open to Paid
        log.append("Invoice from Open to Paid")
        
        #from wizard_pay_invoice.py
        log.append("-getting account.period")
        ids = self.pool.get('account.period').find(cr, uid, None)
        period_id = False
        if len(ids):
            period_id = ids[0]
        else:
            log.append("NO ACCOUNT PERIOD AVAILABLE - SKIP invoice payment")
            return False
          
        invoice = self.pool.get('account.invoice').browse(cr, uid, erp_invoice_id)
        # Need to change partner
        log.append("Make customer reconcilable")
        data = {'reconcile': True}
        self.pool.get('account.account').write(cr, uid, [invoice.partner_id.property_account_receivable.id], data)
          
        amount = invoice.amount_total
        ecriture_name = 'Paiement effectue'
        journals = self.pool.get('account.journal').search(cr, uid, [("code" , "=" , journal_code)])
        if len(journals) > 0:
            journal_id = journals[0]
        else:
            self.pool.get('account.journal').create_payment_methods(cr, uid, [])
            journals = self.pool.get('account.journal').search(cr, uid, [("code" , "=" , journal_code)])
            journal_id = journals[0]
        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, None)
          
        writeoff_account_id = False
        writeoff_journal_id = False
        context={'date_p': invoice_created_at, 'comment':''}
        acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
        if acc_id == []:
            log.append("The journal does not have default credit - debit account")
        else:
            self.pool.get('account.invoice').pay_and_reconcile(cr,uid,[erp_invoice_id], amount, acc_id, period_id, journal_id, writeoff_account_id, period_id, writeoff_journal_id, context, ecriture_name)
            log.append("Payment done")
            
        return True
        
    
    ##################################################################          
    # Credit memo import
    ##################################################################    
    def import_credit_memos(self, cr, uid):
        log.define(self.pool.get('sneldev.logs'), cr, uid)
        wf_service = netsvc.LocalService('workflow')
        if (export_is_running() == False):
            try:
                log.append('===== Credit memo import')
                ids = self.pool.get('sneldev.magento').search(cr, uid, [])
                magento_params = self.pool.get('sneldev.magento').get_magento_params(cr, uid)
                if not magento_params[0].import_credit_memos:
                    log.append('Credit memo import disabled')   
                    set_export_finished()
                    return 0
                
                self.pool = pooler.get_pool(cr.dbname) 
                [status, server, session] = magento_connect(self, cr, uid)
                if not status:
                    log.append('Cannot connect ' + str(server))   
                    set_export_finished()  
                    return -1
                log.append('Logged in to Magento')
            
                #get all credit memos from Magento created after last sync date
                listcreditmemos = server.call(session,'creditmemoapi.list', [{'entity_id': {'gt': magento_params[0].last_creditmemo_id}}])
            
                credits_memos = []
                log.append("Found " + str(len(listcreditmemos)) + " credit memos: id - order_id - created_at")
                for cm in listcreditmemos:
                    log.append("credit_memo:" + cm['increment_id'] + " - " + cm['order_id'] + " - " + cm['created_at'])
                    credits_memos.append({ 'creditmemo_id' : cm['creditmemo_id'],'increment_id' : cm['increment_id'] , 'order_id' : cm['order_id'] , 'created_at' : cm['created_at']} )
             
                new_last_creditmemo_id = magento_params[0].last_creditmemo_id
            except:
                log.append('Could not retreive Magento credit memos. Did you install the Magento module ?')
                set_export_finished()  
                return -1
                
            try:                
                for credits_memo in credits_memos:
                    #get invoice id whose origine is the related order
                    new_last_creditmemo_id = max(int(new_last_creditmemo_id), int(credits_memo['creditmemo_id']))
                    id_orders_related_to_cm = self.pool.get('sale.order').search(cr, uid, [('magento_id', '=', credits_memo['order_id'])])
                    if (id_orders_related_to_cm == []):
                        #Skip
                        log.append("\tOrignial Magento order was not imported :" + str(credits_memo['order_id']))
                        continue
            
                    order = self.pool.get('sale.order').browse(cr, uid, id_orders_related_to_cm[0], None)
                    id_invoices_related_to_order = self.pool.get('account.invoice').search(cr, uid, [('origin', '=', order['name'])])
                    if (id_invoices_related_to_order == []):
                        #Skip
                        log.append("\tNo invoice with origin:" + order['name'])
                        continue
    
                    # Current date and period       
                    period_ids = self.pool.get('account.period').find(cr, uid, credits_memo['created_at'][:10])
                    date = credits_memo['created_at'][:10]
                    description = 'credit memo' + str(credits_memo['increment_id'])
                    period = period_ids[0]
                    log.append("\tCreate Refund Invoice for invoice " + str(id_invoices_related_to_order))
                    for inv in self.pool.get('account.invoice').browse(cr, uid, id_invoices_related_to_order):
                        journal_id = inv.journal_id.id
                        refund_id = self.pool.get('account.invoice').refund(cr, uid, [inv.id], date, period, description, journal_id)
                        #self.pool.get('account.invoice').write(cr, uid, [refund_id], {'date_due': date, 'check_total': inv.check_total})
                        self.pool.get('account.invoice').button_compute(cr, uid, refund_id)
                    # Get payment method from original invoice
                    invoices_related_to_order = self.pool.get('account.invoice').browse(cr, uid, id_invoices_related_to_order)
                    if len(invoices_related_to_order[0].payment_ids) > 0:
                        journal_code = invoices_related_to_order[0].payment_ids[0].journal_id.code
                    else:
                        journal_code = 'checkmo'
                    #self.pool.get('sneldev.magento')._invoice_from_draft_to_paid(cr,uid, id,credits_memo['created_at'], str(credits_memo['increment_id']), journal_code)
      
                    # Return products
                    log.append("\tReturning goods for " + invoices_related_to_order[0].origin)
                    package_ids = self.pool.get('stock.picking').search(cr, uid, [('origin', '=', invoices_related_to_order[0].origin), ('type', '=', 'out')])
                    date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
                    for package_id in package_ids:
                        package = self.pool.get('stock.picking').browse(cr, uid, package_id)
                        if not package.state == 'done':
                            wf_service.trg_validate(uid, 'stock.picking', package_id, 'button_cancel', cr)
                        else:
                            log.append("\tReturning ID " + str(package_id))
                            new_picking = self.pool.get('stock.picking').copy(cr, uid, package_id, {'name': package.name, 'state':'draft', 'type':'in', 'move_lines':[], 'date':date_cur})
                            log.append("\tNew ID " + str(new_picking))
                            for move in package.move_lines:
                                new_move = self.pool.get('stock.move').copy(cr, uid, move.id, {
                                    'picking_id':new_picking,
                                    'state':'draft',
                                    'date':date_cur,
                                    'location_id':move.location_dest_id.id,
                                    'location_dest_id':move.location_id.id,
                                    'date_planned':date_cur,})
                            self.pool.get('stock.picking').draft_validate(cr, uid, [new_picking], [])
        
                log.append("Last credit memo id " + str(new_last_creditmemo_id))
                self.pool.get('sneldev.magento').write(cr, uid, [magento_params[0].id], {'last_creditmemo_id':new_last_creditmemo_id})  
                set_export_finished()  
                return 0
            except: 
                log.print_traceback()  
                set_export_finished()  
                return -1
        log.append('Import already running') 
        return 0
                                  
sneldev_magento()

# Categories
class product_category(osv.osv):
    _name = 'product.category'
    _inherit ='product.category'
    _columns = {
      'modified':fields.boolean('Modified since last synchronization'),
      'magento_id':fields.integer('Magento ID'),
      'export_to_magento': fields.boolean('Export to Magento'),
    }
    
    _defaults = {
        'modified': lambda *a: True,
        'magento_id': lambda *a: -1,
        'export_to_magento': lambda *a: False,
    }
    
    def write(self, cr, uid, ids, vals, context={}):
        if not vals.has_key('modified'):
          vals['modified'] = True
        return super(product_category, self).write(cr, uid, ids, vals, context)    
        
product_category()

# Products
class product_product(osv.osv):
    _name = 'product.product'
    _inherit ='product.product'

    def _product_qty_magento(self, cr, uid, ids, name, arg, context={}):
        qtys = super(product_product, self).read(cr,uid,ids,['qty_available','virtual_available','incoming_qty','outgoing_qty'],context)
        magento = {}
        for element in qtys:
            magento[element['id']]=element['virtual_available']-element['incoming_qty']
        
        return magento
  
    _columns = {
        'modified':fields.boolean('Modified since last synchronization'),
        'magento_id':fields.integer('Magento ID'),
        'qty_magento': fields.function(_product_qty_magento, method=True, type='float', string='Magento Stock'),
        'export_to_magento': fields.boolean('Export to Magento'),    
    }
    
    _defaults = {
        'modified': lambda *a: True,
        'magento_id': lambda *a: -1,
        'export_to_magento': lambda *a: False,
    }
    
    def write(self, cr, uid, ids, vals, context={}):
        if not vals.has_key('modified'):
            vals['modified'] = True
        return super(product_product, self).write(cr, uid, ids, vals, context)    
        
product_product()

# Sale orders
class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    _columns = {
        'magento_id' : fields.integer('Magento ID')
    }
sale_order()

class res_partner_address(osv.osv):
    _name = 'res.partner.address'
    _inherit = 'res.partner.address'
    
    _columns = {
        'magento_company':fields.char('Workplace',size=128)
    }
res_partner_address()

# Partner
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
            
    _columns = {
        'magento_id':fields.integer('Magento ID'),
        'email':fields.char('Email', size=128),
        'export_to_magento': fields.boolean('Export to Magento'),    
        'magento_company': fields.char('Workplace',size=128),
    }
      
    _defaults = {
        'magento_id': lambda *a: -1,
        'export_to_magento': lambda *a: False,        
    }

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
