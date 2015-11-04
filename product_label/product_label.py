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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    label_packaging = fields.Float(
        'Label Packaging', related='product_variant_ids.label_packaging',
        digits=dp.get_precision('Product Unit of Measure'))
    label_uom_id = fields.Many2one(
        'product.uom', string='Label UoM',
        related='product_variant_ids.label_uom_id')
    product_label_pricelist_id = fields.Many2one(
        'product.pricelist', string='Label Pricelist', company_dependent=True)
    product_label_tax_ids = fields.Many2many(
        'account.tax', string='Label Taxes')


class Product(models.Model):

    _inherit = 'product.product'

    @api.model
    def _get_label_uom_id(self):
        uom = self.env['product.uom'].search([], limit=1, order='id')
        return uom or False

    @api.one
    # @api.depends('product_label_pricelist_id')
    def _compute_label_prices(self):
        if self.product_label_pricelist_id:
            label_price = self.product_label_pricelist_id.price_get(
                self.id, 1, None)[self.product_label_pricelist_id.id]
        else:
            label_price = self.lst_price
        if self.product_label_tax_ids:
            tmp = self.product_label_tax_ids.compute_all(
                label_price, 1, product=self.id)
            label_price = tmp['total_included']
        self.label_price = label_price
        if not self.label_packaging:
            self.label_price_per_uom = label_price
        else:
            self.label_price_per_uom = label_price / self.label_packaging

    label_price = fields.Float(
        'Label Price', digits=dp.get_precision('Product Price'),
        compute='_compute_label_prices')
    label_price_per_uom = fields.Float(
        'Price per UoM', digits=dp.get_precision('Product Price'),
        compute='_compute_label_prices')
    label_packaging = fields.Float(
        'Label Packaging', digits=dp.get_precision('Product Unit of Measure'),
        default=1)
    label_uom_id = fields.Many2one(
        'product.uom', string='Label UoM', default=_get_label_uom_id)
