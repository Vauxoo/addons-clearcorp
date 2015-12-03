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
from openerp import models, fields
import openerp.addons.decimal_precision as dp

class stock_move_thread(models.Model):
    
    _inherit = ['stock.move', 'mail.thread']
    _name = "stock.move"
    _description = "Stock Move"
    _order = 'date_expected desc, id'
    _log_create = False
    
    product_id= fields.Many2one('product.product', 'Product', required=True, select=True, domain=[('type', '<>', 'service')], states={'done': [('readonly', True)]}, track_visibility='onchange')
    product_uom_qty= fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True, states={'done': [('readonly', True)]}, track_visibility='onchange',
            help="This is the quantity of products from an inventory "
                "point of view. For moves in the state 'done', this is the "
                "quantity of products that were actually moved. For other "
                "moves, this is the quantity of product that is planned to "
                "be moved. Lowering this quantity does not generate a "
                "backorder. Changing this quantity on assigned moves affects "
                "the product reservation, and should be done with care."
        )