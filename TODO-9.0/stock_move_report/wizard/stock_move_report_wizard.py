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
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

import time

class StockMoveWizard(models.TransientModel):
    _name = 'stock.move.report.wiz'
   
    @api.multi
    def print_report(self):
        category_list_ids=[]
        product_list_ids=[]
        res={}
        if not self.product_ids and not self.category_ids:
            doc_ids = self.env['product.product'].search([], order="default_code ASC")
        else:
            category_list_ids=[]
            product_list_ids=[]
            for category in self.category_ids:
                category_list_ids.append(category.id)
            for product in self.product_ids:
                product_list_ids.append(product.id)
            doc_ids = self.env['product.product'].search(['|',('id','in',product_list_ids),('product_tmpl_id.categ_id','in',category_list_ids)] , order="default_code ASC")
        data={}
        data['form']=self.read(['date_from','date_to','include_costs','category_ids','product_ids','partner_ids','source_location_ids','destination_location_ids', 'picking_type_ids'])[0]

        if self.out_format=='qweb-PDF':
            res = self.env['report'].get_action(doc_ids,
            'stock_move_report.report_stock_move_pdf', data=data)
            return res
        elif self.out_format=='qweb-XLS':
            res = self.env['report'].get_action(doc_ids,
            'stock_move_report.report_stock_move_xls', data=data)
            return res

    date_from=fields.Date(string='Start Date',required=True)
    date_to=fields.Date(string='End Date',required=True)
    include_costs=fields.Boolean(string='Include costs')
    category_ids=fields.Many2many('product.category',relation='product_category_stock_move_report_wiz_rel',string='Category Product')
    product_ids=fields.Many2many('product.product',relation='product_product_stock_move_report_wiz_rel',string='Product')
    partner_ids = fields.Many2many('res.partner',relation='res_partner_stock_move_report_wiz_rel',string='Company')
    source_location_ids=fields.Many2many('stock.location',relation='stock_location_stock_move_report_wiz_source_rel',string='Source Locations')
    destination_location_ids=fields.Many2many('stock.location',relation='stock_location_stock_move_report_wiz_dest_rel',string='Destination Locations')
    picking_type_ids = fields.Many2many('stock.picking.type',relation='stock_picking_type_stock_move_report_wiz_dest_rel',string='Picking Type')
    out_format=fields.Selection([('qweb-PDF', 'Portable Document Format (.pdf)'), ('qweb-XLS','Microsoft Excel 97/2000/XP/2003 (.xls)')], string="Print Format",required=True)
    
    _defaults={
              'out_format':'qweb-PDF',
              'include_costs': False,
              }