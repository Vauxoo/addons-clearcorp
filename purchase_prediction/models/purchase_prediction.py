# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime

from openerp import fields, models, _, api
from openerp.exceptions import Warning


class PurchasePrediction(models.Model):
    _name = "purchase.prediction"
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('purchase.prediction')
        res = super(PurchasePrediction, self).create(vals)

        #~ Instances
        prod_list = []

        prod_obj = self.env['product.product']
        stock_picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        prediction_line_obj = self.env['purchase.prediction.line']
        supplier_info_obj = self.env['product.supplierinfo']
        start_month = datetime.strptime(vals['start_date'],'%Y-%m-%d')
        end_month = datetime.strptime(vals['end_date'],'%Y-%m-%d')
        
        if start_month >= end_month:
            raise Warning(_('Check the start and end dates.'))
        
        months_qty = (end_month.year - start_month.year) * 12 + end_month.month - start_month.month

        supplier_info_list = supplier_info_obj.search([('name','=',vals['partner_id'])])
        stock_picking_in_list = stock_picking_obj.search([('date','>=',vals['start_date']),('date','<=',vals['end_date']),('picking_type_id.code','=','incoming'),('state','=','done')])
        stock_picking_out_list = stock_picking_obj.search([('date','>=',vals['start_date']),('date','<=',vals['end_date']),('picking_type_id.code','=','outgoing'),('state','=','done')])
        stock_picking_int_list = stock_picking_obj.search([('date','>=',vals['start_date']),('date','<=',vals['end_date']),('picking_type_id.code','=','internal'),('state','=','done')])

        for supplier_info in supplier_info_list:
            prod_list.append(supplier_info.product_tmpl_id)
               
        for product in prod_list:

            # Si el product_id en la tabla product_supplierinfo no es el 
            # id de la tabla product_product entonces es el product_tpml_id
            # por lo tanto buscamos el producto por el product_tpml_id
            # para que la busqueda no de un error
            try:
                logging.getLogger("Name").info(product.name)
            except:
                p_id = prod_obj.search([('product_tmpl_id','=', product.id),])
                p = prod_obj.browse(p_id)
                product = p[0]

            qty_purchase = 0
            qty_sold = 0
            qty_proyect = 0

            stock_move_in_list = stock_move_obj.search([('state','=','done'),('product_id','=',product.id),('picking_id','in',stock_picking_in_list._ids),('date','>=',vals['start_date']),('date','<=',vals['end_date'])])
            stock_move_out_list = stock_move_obj.search([('state','=','done'),('product_id','=',product.id),('picking_id','in',stock_picking_out_list._ids),('date','>=',vals['start_date']),('date','<=',vals['end_date'])])
            stock_move_int_list = stock_move_obj.search([('state','=','done'),('product_id','=',product.id),('picking_id','in',stock_picking_int_list._ids),('date','>=',vals['start_date']),('date','<=',vals['end_date'])])

            # Purchase qty
            for move in stock_move_obj.browse(stock_move_in_list):
                qty_purchase = qty_purchase + move.product_qty

            # Sold qty
            for move in stock_move_obj.browse(stock_move_out_list):
                qty_sold = qty_sold + move.product_qty

            # Used in MRP Production
            for move in stock_move_obj.browse(stock_move_int_list):
                qty_proyect = qty_proyect + move.product_qty
            
            try:
                if product.virtual_available < product.qty_available:
                    qty_approved = ((qty_sold + qty_proyect - product.qty_available) / months_qty) * vals['prediction_month_qty']           
                else:
                    qty_approved = ((qty_sold + qty_proyect - product.virtual_available) / months_qty) * vals['prediction_month_qty']
            except:
                qty_approved = 0
            
            data = {
            'product_id': product.id,
            'name': self.env['ir.sequence'].get('purchase.prediction'),
            'qty_sold' : qty_sold,
            'qty_purchase': qty_purchase,
            'qty_proyect': qty_proyect,
            'qty_approved': qty_approved,
            'prediction_id': res.id
            }
            
            prediction_line_obj.create(data)

        return res

    _name = "purchase.prediction"

    name = fields.Char('Name', size=64, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Supplier', required=True)
    prediction_month_qty = fields.Float('Month Quantities')
    prediction_id = fields.One2many('purchase.prediction.line',
                                    'prediction_id', 'Products')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    create_date = fields.Datetime('Creation Date', readonly=True)

