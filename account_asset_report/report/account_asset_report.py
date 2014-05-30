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
            'display_partner_name':self.display_partner_name, 
            'display_state':self.display_state,
            'display_category_name':self.display_category_name, 
            'set_data_template': self.set_data_template,
            'get_category_order':self.get_category_order,
            'exist_asset_by_category':self.exist_asset_by_category, 
            'get_amortized_value':self.get_amortized_value,
            'get_last_depreciation_date':self.get_last_depreciation_date,
            'set_total_result_by_category':self.set_total_result_by_category, 
        })
    
    #=========== SET AND GET DATA ==============================================
    def get_state(self, data):
        return self._get_form_param('state', data)
    
    def get_partner_id(self, data):
        return self._get_info(data,'partner_id', 'res.partner')
    
    def get_category_ids(self, data):
        return self._get_info(data,'category_asset_ids', 'account.asset.category')
          
    def exist_asset_by_category(self, category_id):
        if category_id in self.localcontext['storage']['result'].keys():
            return True
        else:
            return False
    
    #set data to use in odt template. 
    def set_data_template(self, data):        
        result = self.classified_account_assets(data)        
        dict_update = {'result': result,}        
        self.localcontext['storage'].update(dict_update)
        return False
    
    #============== DISPLAY DATA ===============================================    
    def display_partner_name(self, data):
        partner = self.get_partner_id(data)
        if partner:
            return partner.name
        else:
            return _('No partner')
    
    def display_state(self, data):
        state = self.get_state(data)
        if state == 'draft':
            return _('Draft')
        elif state == 'open':
            return _('Open')
        elif state =='close':
            return _('Close')
        else:
            return _('All states')
        
    def display_category_name(self, data):
       name = ''
       
       if not self.get_category_ids(data): #It means that non-one was selected
           return _('All categories')
       else:
           categories = self.get_category_ids(data)
           for category in categories:
               name += category.name + ', '
           return name
        
    #===========================================================================
    
    """1. Build a domain with all search criteria (this is for account_assets) """
    def build_search_criteria(self, data):
        list_tuples = []
        category_ids = []

        #******State
        if self.get_state(data):
            state = self.get_state(data)
            domain = ('state', '=', state)
            list_tuples.append(domain)
    
        #******Partner 
        partner_id = self.get_partner_id(data) #browse_record m2o
        if partner_id:
            domain = ('partner_id.id','in', [partner_id])
            list_tuples.append(domain)
        
        #******Categories 
        categories_ids = self.get_category_ids(data) #browse_record m2m
        if not categories_ids:
            categories_ids = self.pool.get('account.asset.category').search(self.cr, self.uid, [])
            domain = ('category_id.id','in', categories_ids)
        else:
            for category in self.get_category_ids(data):
                category_ids.append(category.id)
            domain = ('category_id.id','in', category_ids)
        list_tuples.append(domain)
        
        return list_tuples
    
    """2. Get account_assets that match with domain """
    def get_account_assets(self, data):
        
        #Search criteria
        domain = self.build_search_criteria(data)        
        #Find assets
        account_asset_ids = self.pool.get('account.asset.asset').search(self.cr, self.uid, domain, order = 'name ASC')
        account_asset_obj = self.pool.get('account.asset.asset').browse(self.cr, self.uid, account_asset_ids)
        
        return account_asset_obj
    
    """3. Classified account_asset in 1 levels: Category Assets """
    def classified_account_assets(self, data):
        res = {}
        #Get account_assets
        account_assets = self.get_account_assets(data)
        
        for asset in account_assets:
            if asset.category_id.id not in res.keys():
                res[asset.category_id.id] = []
            res[asset.category_id.id].append(asset)
        return res
    
    #Order alphabetically asset categories
    def get_category_order(self, data):
        order_list = []
        result = {}

        category_list = self.get_category_ids(data)
        if category_list:            
            for category in self.get_category_ids(data):
                order_list.append(category.id)
            order_ids = self.pool.get('account.asset.category').search(self.cr, self.uid, [('id','in',order_list)], order='name ASC')
        else:
            order_ids = self.pool.get('account.asset.category').search(self.cr, self.uid, [], order='name ASC')
            
        order_obj = self.pool.get('account.asset.category').browse(self.cr, self.uid, order_ids)    
       
        return order_obj
    
    def get_amortized_value(self, asset):
        return asset.purchase_value - asset.value_residual
    
    def get_last_depreciation_date(self, cr, uid, ids, context=None):
        """
        @param id: ids of a account.asset.asset objects
        @return: Returns a dictionary of the effective dates of the last depreciation entry made for given asset ids. If there isn't any, return the purchase date of this asset
        """
        cr.execute("""
            SELECT a.id as id, COALESCE(MAX(l.depreciation_date),a.purchase_date) AS date
            FROM account_asset_asset a
            LEFT JOIN account_asset_depreciation_line l ON (l.asset_id = a.id)
            WHERE a.id IN %s
            GROUP BY a.id, a.purchase_date """, (tuple(ids),))
        return dict(self.cr.fetchall())
    
    def set_total_result_by_category(self, category_id):
        totals = {'purchase_value':0.0, 'amortized_value':0.0, 'residual_value':0.0}
        
        for asset in self.get_data_template('result')[category_id]:
            totals['purchase_value'] += asset.purchase_value
            totals['amortized_value'] += self.get_amortized_value(asset)
            totals['residual_value'] += asset.value_residual
        
        dict_update = {'totals': totals,}        
        self.localcontext['storage'].update(dict_update)
        return False