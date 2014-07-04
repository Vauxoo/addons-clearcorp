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
from numpy.ma.core import ids

class Parser(accountReportbase):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
           'cr' : cr,
           'uid': uid,
           'storage':{},
           'display_taxes':self.display_taxes,
           'get_order_taxes':self.get_order_taxes,
           'get_tax_name': self.get_tax_name, 
           'get_data_block_tax': self.get_data_block_tax, 
           'compute_total_block':self.compute_total_block
        })
    
    #---------SET AND GET DATA ----------#
    # Get taxes from wizard
    def get_taxes(self, data):
        return self._get_info(data,'account_tax_ids', 'account.tax')
    
    #Get taxes order by name
    def get_order_taxes(self, data):
        taxes_ids = []
        
        if not self.get_taxes(data):
            taxes_ids = self.pool.get('account.tax').search(self.cr, self.uid, [], order="name ASC")
            return self.pool.get('account.tax').browse(self.cr, self.uid, taxes_ids)
        else:
           return self.get_taxes(data) #browse record list
    
    #Extract ids from taxes
    def get_taxes_ids(self, data):
        ids = []
        if self.get_taxes(data):
            for tax in self.get_taxes(data):
                ids.append(tax.id)
        return ids
    
    def get_tax_name(self, tax_id):
        name = ''
        tax = self.pool.get('account.tax').browse(self.cr, self.uid, tax_id)
        
        if tax.type == 'percent' or tax.type == 'fixed':
            tax_amount = 100 * tax.amount
            name = tax.name + ' - ' + str(tax_amount) + '%'
        else:
            name = tax.name
            
        return name
    
    #================ DISPLAY DATA ===========================#
    def display_taxes(self, data):
       name = ''
       
       if not self.get_taxes(data): #It means that non-one was selected
           return _('All taxes')
       else:
           taxes = self.get_taxes(data)
           for tax in taxes:
               name += tax.name + ', '
           return name  
    
    #========= BUILD DATA
    def get_invoices(self, tax_id, data):
        account_invoice_obj = self.pool.get('account.invoice')
        result={}
        domain = []
        
        date_from = self.get_date_from(data)
        date_to = self.get_date_to(data)        
        domain.append(('date_invoice', '>=', date_from))
        domain.append(('date_invoice', '<=', date_to))

        tuple = ('invoice_line.invoice_line_tax_id', 'in', tax_id)
        domain.append(tuple)
        
        tuple = ('state', '!=', 'draft')
        domain.append(tuple)
        
        invoices_ids = account_invoice_obj.search(self.cr, self.uid, domain, context=None)
        invoices_obj = account_invoice_obj.browse(self.cr, self.uid, invoices_ids, context=None)
        
        return invoices_obj
    
    """
        1. Create a structure like this:
            tax_block[tax_id] = {} (invoices)
            
            Then invoices is a dictionary, where key is id invoice and each key
            has a list with lines that its tax match with tax_id that is passed
            as a parameter
            
            So, iterate dictionary like this
            
            for tax_id, invoice in tax_block.iteritems():
                tax_id ...
                for invoices in invoices:
                    for line in invoices['lines']:
                        (line as a dictionary)        
    """
    
    def get_invoices_lines_to_process(self, tax_id, data):
        line_info = {}
        invoice_dict = {}
        tax_block = {}     
        qty_lines = 0   
        list = []
        
        add_invoice = False
        
        for invoice in self.get_invoices(tax_id, data):
            line_info = {}
            invoice_dict = {}
            qty_lines = 0 #this variable is per invoice
            
            for line in invoice.invoice_line:
                added_line = False
                for tax in line.invoice_line_tax_id:
                    if tax.id == tax_id:               
                        qty_lines += 1
                        invoice_dict[invoice.id] = {'lines':[],}       
                        add_invoice = True     
                        
                        if len(invoice_dict[invoice.id]['lines']) > 0:
                            for dict in invoice_dict['lines']:
                                if line.id == dict['id']:
                                    added_line = True
                            
                            if not added_line:
                                #compute taxes
                                price = line.price_unit * (1-(line.discount or 0.0)/100.0)  
                                amount_tax = self.pool.get('account.tax').compute_all(self.cr, self.uid, [tax], price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
                                
                                line_info['id'] = line.id
                                line_info['price_sub_not_dis'] = line.price_subtotal_not_discounted
                                line_info['price_subtotal'] = line.price_subtotal, 
                                line_info['taxes'] = amount_tax['total_included'] - line.price_subtotal
                            
                        else:
                            #compute taxes
                            price = line.price_unit * (1-(line.discount or 0.0)/100.0)  
                            #amount_tax is a dictionary
                            amount_tax = self.pool.get('account.tax').compute_all(self.cr, self.uid, [tax], price,  line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
                            
                            line_info['id'] = line.id
                            line_info['price_sub_not_dis'] = line.price_subtotal_not_discounted
                            line_info['price_subtotal'] = line.price_subtotal,
                            line_info['taxes'] = amount_tax['total_included'] - line.price_subtotal
                            
                        invoice_dict[invoice.id]['lines'].append(line_info)                
                        
            
            if add_invoice:
                 invoice_dict[invoice.id].update({
                                   'number': invoice.number, 
                                   'client': invoice.partner_id.name or '', 
                                   'qty_lines': qty_lines,
                                   'qty_lines_total': len(invoice.invoice_line),
                                   'type': invoice.type, 
                                   })
                 list.append(invoice_dict)
                 add_invoice = False
                
        tax_block[tax_id] = {}
        tax_block[tax_id].update({'invoices': list})
        
        return tax_block
    
    #========== COMPUTE DATA
    def get_price_subtotal_not_discounted_per_invoice(self, invoice):
        price_subtotal_not_discount =  0.0
    
        for line in invoice['lines']:
            price_subtotal_not_discount += line['price_sub_not_dis']
    
        return price_subtotal_not_discount
    
    def get_price_subtotal_per_invoice(self, invoice):
        price_subtotal =  0.0        
        
        for line in invoice['lines']:
            price_subtotal += line['price_subtotal'][0]
        
        return price_subtotal
    
    def get_discount_per_invoice(self, invoice):
        discount = 0.0
        price_subtotal =  0.0
        price_subtotal_not_discount =  0.0
        
        price_subtotal_not_discount = self.get_price_subtotal_not_discounted_per_invoice(invoice)
        price_subtotal = self.get_price_subtotal_per_invoice(invoice)
        
        discount = price_subtotal_not_discount -  price_subtotal
        
        return discount
    
    def get_taxes_per_invoice(self, invoice):
        taxes =  0.0        
        
        for line in invoice['lines']:
            taxes += line['taxes']
        
        return taxes
    
    #============== FINAL FUNCTION
    def set_data_template(self, tax_id, data):        
        #Invoices and lines are processing in this function 
        tax_block = self.get_invoices_lines_to_process(tax_id, data)      
        
        dict_update = {
                       'tax_block': tax_block,
                       'final_list': [],
                       } 
        
        self.localcontext['storage'].update(dict_update)
        return False
    
    def get_data_block_tax(self, tax_id):        
        final_block = {}
        final_list = []  
  
        for element in self.get_data_template('tax_block')[tax_id]['invoices']:
            for id, invoice in element.iteritems():
                final_block = {}
                if invoice['type'] == 'out_refund' or invoice['type'] == 'in_refund':
                    final_block['invoice_number'] = invoice['number']
                    final_block['client'] = invoice['client']
                    final_block['qty_lines'] = str(invoice['qty_lines']) + "/" + str(invoice['qty_lines_total'])
                    final_block['subtotal_without_dis'] = -1 * self.get_price_subtotal_not_discounted_per_invoice(invoice)
                    discount = self.get_discount_per_invoice(invoice)
                    if discount > 0:
                        final_block['discount'] = -1 * discount
                    else:
                        final_block['discount'] = discount
                    final_block['subtotal_dis'] = -1 * self.get_price_subtotal_per_invoice(invoice)
                    final_block['taxes'] = -1 * self.get_taxes_per_invoice(invoice)
                    final_block['total'] = final_block['subtotal_dis'] + final_block['taxes']
                else:
                    final_block['invoice_number'] = invoice['number']
                    final_block['client'] = invoice['client']
                    final_block['qty_lines'] = str(invoice['qty_lines']) + "/" + str(invoice['qty_lines_total'])                
                    final_block['subtotal_without_dis'] = self.get_price_subtotal_not_discounted_per_invoice(invoice)
                    final_block['discount'] = self.get_discount_per_invoice(invoice)
                    final_block['subtotal_dis'] = self.get_price_subtotal_per_invoice(invoice)
                    final_block['taxes'] = self.get_taxes_per_invoice(invoice)
                    final_block['total'] = final_block['subtotal_dis'] + final_block['taxes']                
                
                final_list.append(final_block)
        
        dict_update = {'final_list': final_list}
        self.localcontext['storage'].update(dict_update)
        
        return final_list
    
    def compute_total_block(self):
        totals = {
                  'subtotal_without_dis': 0.0,
                  'discount':0.0,
                  'subtotal_dis':0.0,
                  'taxes': 0.0, 
                  'total': 0.0,
                  }
        
        for element in self.get_data_template('final_list'):
            totals['subtotal_without_dis'] += element['subtotal_without_dis']
            totals['discount'] += element['discount']
            totals['subtotal_dis'] += element['subtotal_dis']
            totals['taxes'] += element['taxes']
            totals['total'] += element['total']
        
        dict_update = {'totals': totals}
        self.localcontext['storage'].update(dict_update)
        
        return False
            