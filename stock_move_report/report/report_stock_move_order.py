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


from openerp import models
from openerp.report import report_sxw


class StockMoveOder(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(StockMoveOder, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_data': self.get_data,
            'cr': cr,
            'uid': uid,
        })

    def get_data(self, cr, uid, data):
        product_product_obj = self.pool.get('product.product')
        sale_line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        purchase_obj = self.pool.get('purchase.order')
        product_ids = data['form']['product_ids']
        stock_location = data['form']['stock_location'][0]
        product_lines_to_print = []

        for product_id in product_ids:
            product = product_product_obj.browse(self.cr,
                                                 self.uid, product_id,
                                                 context=self.localcontext)[0]
            sale_line_ids = sale_line_obj.search(self.cr,
                                                 self.uid,
                                                 [('product_id',
                                                   '=',
                                                   product_id),
                                                  ('order_id.shipped',
                                                   '=',
                                                   False)]
                                                 )
            sale_order_ids = sale_obj.search(
                self.cr,
                self.uid,
                [('order_line',
                  'in',
                  sale_line_ids)]
                )
            sale_orders = sale_obj.browse(self.cr, self.uid, sale_order_ids)
            sale_orders_list = []
            purchase_line_ids = purchase_line_obj.search(self.cr,
                                                         self.uid,
                                                         [('product_id',
                                                           '=',
                                                           product_id),
                                                          ('order_id.shipped',
                                                           '=',
                                                           False)]
                                                         )
            purchase_order_ids = purchase_obj.search(self.cr,
                                                     self.uid,
                                                     [('order_line',
                                                       'in',
                                                       purchase_line_ids)]
                                                     )
            purchase_orders = purchase_obj.browse(self.cr, self.uid,
                                                  purchase_order_ids,
                                                  context=self.localcontext)
            for sale_order in sale_orders:
                sale_product_quantity = 0.0
                for sale_order_line in sale_order.order_line:
                    if sale_order_line.product_id.id == product_id:
                        sale_product_quantity += \
                            sale_order_line.product_uom_qty
                for picking in sale_order.picking_ids:
                    for move in picking.move_lines:
                        if move.product_id.id == product_id and \
                                move.location_id.id == stock_location and \
                                move.state == 'done':
                            sale_product_quantity -= \
                                move.product_uom_qty
                if sale_product_quantity != 0.0:
                    sale_order_line_dict = {'sale': sale_order.name,
                                            'quantity': sale_product_quantity,
                                            }
                    sale_orders_list.append(sale_order_line_dict)
            context = {'location': stock_location}
            line = {
                'name': product.name,
                'product': product,
                'qyt_available':
                    product_product_obj._product_available(
                        self.cr, self.uid, [product_id], field_names=None,
                        arg=False,  context=context)
                    [product_id]['qty_available'],
                'virtual_available':
                    product_product_obj._product_available(
                        self.cr, self.uid, [product_id], field_names=None,
                        arg=False,  context=context)
                    [product_id]['virtual_available'],
                'product_lines': [],
                }
            # is product are in purchase
            purchase_orders_list = []
            for purchase_order in purchase_orders:
                purchase_product_quantity = 0.0
                for purchase_order_line in purchase_order.order_line:
                    if purchase_order_line.product_id.id == product_id:
                        purchase_product_quantity +=\
                            purchase_order_line.product_qty
                for picking in purchase_order.picking_ids:
                    for move in picking.move_lines:
                        if move.product_id.id == product_id and\
                                move.location_dest_id.id == stock_location and\
                                move.state == 'done':
                            purchase_product_quantity -=\
                                move.product_uom_qty
                if purchase_product_quantity != 0.0:
                    purchase_order_line_dict = {
                        'purchase': purchase_order.name,
                        'quantity': purchase_product_quantity,
                        }
                    purchase_orders_list.append(purchase_order_line_dict)
            product_lines = []
            product_lines.append(sale_orders_list)
            product_lines.append(purchase_orders_list)
            line['product_lines'] = product_lines
            product_lines_to_print.append(line)
        return product_lines_to_print


class report_stock_move_order(models.AbstractModel):
    _name = 'report.stock_move_report.report_stock_move_order'
    _inherit = 'report.abstract_report'
    _template = 'stock_move_report.report_stock_move_order'
    _wrapped_report_class = StockMoveOder
