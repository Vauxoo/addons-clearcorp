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
from openerp import models, fields, api, _

class ProductInvoiceWizard(models.TransientModel):

    _name = 'product.invoice.report.wizard'

    @api.one
    @api.constrains('date_from','date_to')    
    def _check_filter_date(self):
        if self.filter=='filter_date':
            if self.date_from>self.date_to:
                raise Warning(_('Start Date must be less than End Date'))
    @api.constrains('period_from','period_to')        
    def _check_filter_period(self):
        if self.filter=='filter_period':
            if self.period_from.date_start>self.period_to.date_stop:
                raise Warning(_('Start Period must be less than End Period'))
    
    @api.multi
    def print_report(self):
        #Get all customers if no one is selected
        if not self.partner_ids:
            self.partner_ids = self.env['res.partner'].search([('customer','=',True)])
        data = {
            'form': {
                     'sortby': self.sortby,
                     'filter': self.filter,
                     'date_from': self.date_from,
                     'date_to': self.date_to,
                     'fiscalyear_id': self.fiscalyear_id.id,
                     'period_to': self.period_to.id,
                     'period_from':self.period_from.id,
            }
        }
        if self.out_format=='qweb-PDF':
            res = self.env['report'].get_action(self.partner_ids,
            'product_invoice_report.report_product_invoice_pdf', data=data)
            return res        
        elif self.out_format=='qweb-XLS':
            res = self.env['report'].get_action(self.partner_ids,
            'product_invoice_report.report_product_invoice_xls', data=data)
            return res
    
    out_format=fields.Selection([('qweb-PDF', 'Portable Document Format (.pdf)'), ('qweb-XLS','Microsoft Excel 97/2000/XP/2003 (.xls)')], string="Print Format",required=True)
    sortby=fields.Selection([('sort_date', 'Date'), ('sort_period','Period'), ('sort_partner','Partner'),('sort_product','Product'),('sort_product_category','Product Category')], string="Sort by",required=True)
    filter=fields.Selection([('filter_no', 'No Filter'), ('filter_date','Date'), ('filter_period','Period')], string="Filter",required=True,default='filter_no')
    date_from=fields.Date(string="Start Date")
    date_to=fields.Date(string="End Date")
    fiscalyear_id=fields.Many2one('account.fiscalyear',string="Fiscal Year")
    period_to= fields.Many2one('account.period',string="End Period")
    period_from= fields.Many2one('account.period',string="Start Period")
    partner_ids= fields.Many2many('res.partner',string="Customer")