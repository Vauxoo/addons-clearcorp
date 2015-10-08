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


import time
import operator
import itertools
from datetime import datetime
from openerp import models, api
from openerp.report import report_sxw

class ProductInvoiceReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ProductInvoiceReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                                  'get_sort':self.get_sort,
                                  'get_filter':self.get_filter,
                                  'get_start_period':self.get_start_period,
                                  'get_end_period':self.get_end_period,
                                  'get_date_from':self.get_date_from,
                                  'get_date_to':self.get_date_to,
                                  'get_group_lines':self.get_group_lines,
                                  'get_quantity_group':self.get_quantity_group,
                                  'get_subtotal_group':self.get_subtotal_group,
                                  'get_periods_format_xls':self.get_periods_format_xls,
                                  'get_dates_format_xls':self.get_dates_format_xls
        })

    ############################Read Data#######################################
    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field)
        if info:
            return self.pool.get(model).browse(self.cr, self.uid, info)
        return False
    
    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)

    ############################Report Functions################################
    def get_sort(self, data):
        return self._get_form_param('sortby', data)
    
    def get_filter(self, data):
        return self._get_form_param('filter', data)
    
    def get_start_period(self, data):
        return self._get_info(data,'period_from', 'account.period')
    
    def get_periods_format_xls(self, data):
        return 'Desde: ' + self.get_start_period(data).name + ' Hasta: ' + self.get_end_period(data).name
        
    def get_dates_format_xls(self, data):
        return 'Desde: ' + self.formatLang(self.get_date_from(data),date=True) + ' Hasta: ' + self.formatLang(self.get_date_to(data),date=True)   
      
    def get_end_period(self, data):
        return self._get_info(data,'period_to', 'account.period')
    
    def get_date_from(self, data):
        return self._get_form_param('date_from', data)

    def get_date_to(self, data):
        return self._get_form_param('date_to', data)

    def get_partner_ids(self, active_ids):
        return self.pool.get('res.partner').browse(self.cr, self.uid, active_ids)
    
    #========= BUILD DATA
    def get_search_criteria(self,data,active_ids):
        domain = []
        partner_ids=[]
        #Filters
        #Filter type invoice
        tuple=('invoice_id.type','in',('out_invoice','out_refund'))
        domain.append(tuple)
    
        #Filter type date or period
        if self.get_filter(data)=='filter_date':
            date_from= self.get_date_from(data)
            date_to = self.get_date_to(data)
            domain.append(('invoice_id.date_invoice', '>=', date_from))
            domain.append(('invoice_id.date_invoice', '<=', date_to))
            
        elif self.get_filter(data)=='filter_period':
            #period_from=data['form']['period_from'][0]
            #period_to=data['form']['period_to'][0]
            period_from=self.get_start_period(data)
            period_to=self.get_end_period(data)
           
            domain.append(('invoice_id.period_id.date_start', '>=', period_from.date_start))
            domain.append(('invoice_id.period_id.date_stop', '<=', period_to.date_stop))
            
        #Filter Partners
        partner_list = self.get_partner_ids(active_ids)
        if partner_list:
            for partner in partner_list:
                partner_ids.append(partner.id)
                tuple = ('invoice_id.partner_id', 'in', partner_ids)
            domain.append(tuple)
        return domain    
    
    def get_group_criteria(self,data):
        sort=False
        #sort
        if self.get_sort(data)=='sort_date':
            sort='date_invoice'
        elif self.get_sort(data)=='sort_period':
            sort="period_id"
        elif self.get_sort(data)=='sort_partner':   
            sort="partner_id"
        elif self.get_sort(data)=='sort_product': 
            sort="product_id"
        elif self.get_sort(data)=='sort_product_category':
            sort="categ_id"
        return sort

    def get_invoices_lines(self,data,active_ids):
        invoice_lines_obj = self.pool.get('account.invoice.line')
        domain=[]
        
        domain=self.get_search_criteria(data,active_ids)

        #Create list of dictionaries for the report
        lines_ids = invoice_lines_obj.search(self.cr, self.uid, domain, context=None)
        lines_obj=invoice_lines_obj.browse(self.cr, self.uid, lines_ids, context=None)
        
        return  lines_obj
    
    def get_quantity_group(self,group,data):
        quantity_list=[]
        sum_quantities=0

        for line in group:
            sum_quantities+=line['quantity']
            
        return sum_quantities
    
    def get_subtotal_group(self,group,data):
        subtotal_list=[]
        sum_subtotal=0
            
        for line in group:
            sum_subtotal+=line['subtotal']
        return sum_subtotal
            
    def get_group_lines(self,data,active_ids):
        line_report={}
        quantity_list=[]
        subtotal_list=[]
        products_invoices=[]
        partner_ids=[]
        group_lines=[]
        sort=False
        
        lines_obj=self.get_invoices_lines(data,active_ids)
        for line in lines_obj:
            line_report={}
            line_report['date_invoice']=line.invoice_id.date_invoice
            line_report['period_id']=line.invoice_id.period_id.name
            line_report['number']=line.invoice_id.number
            line_report['partner_id']=line.invoice_id.partner_id.name
            line_report['categ_id']=line.product_id.categ_id.display_name
            if line.product_id:
                line_report['product_id']=line.product_id.name
            else:
                line_report['product_id']=line.name
            line_report['price_unit']=line.price_unit
            line_report['discount']=line.discount
            
            if line.invoice_id.type=="out_refund":
                line_report['quantity']=-(line.quantity)
                line_report['subtotal']=-(line.price_subtotal)
            else:
                line_report['quantity']=line.quantity
                line_report['subtotal']=line.price_subtotal
            
            products_invoices.append(line_report)  
        
        sort=self.get_group_criteria(data)
        
       # product_invoicies_sort=sorted(products_invoices, key=itemgetter(sort))
        products_invoices.sort(key=operator.itemgetter(sort))
        #Sort and group by group criteria
        for key,items in itertools.groupby(products_invoices,operator.itemgetter(sort)):
             group_lines.append(list(items))
              
        return group_lines


class report_product_invoice_pdf(models.AbstractModel):
    _name = 'report.product_invoice_report.report_product_invoice_pdf'
    _inherit = 'report.abstract_report'
    _template = 'product_invoice_report.report_product_invoice_pdf'
    _wrapped_report_class = ProductInvoiceReport
    
class report_product_invoice(models.AbstractModel):
    _name = 'report.product_invoice_report.report_product_invoice_xls'
    _inherit = 'report.abstract_report'
    _template = 'product_invoice_report.report_product_invoice_xls'
    _wrapped_report_class = ProductInvoiceReport