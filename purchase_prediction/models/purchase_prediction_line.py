# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class PurchasePredictionLine(models.Model):
    _name = "purchase.prediction.line"

    name = fields.Char('Name', size=64, readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty_sold = fields.Float('Sales Quantities', readonly=True)
    qty_purchase = fields.Float('Bought Quantities', readonly=True)
    qty_proyect = fields.Float('Project Quantities', readonly=True)
    stock_available = fields.Float(related='product_id.qty_available',
                                   string='Real Stock',
                                   store=False, readonly=True)
    virtual_available = fields.Float(related='product_id.virtual_available',
                                     string='Virtual Stock',
                                     store=False, readonly=True)
    qty_approved = fields.Float('Recommended Quantities')
    prediction_id = fields.Many2one('purchase.prediction', 'Prediction')
