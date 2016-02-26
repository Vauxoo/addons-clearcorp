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


class sale_order_line(models.Model):

    _inherit = "sale.order.line"

    #@api.one
    @api.onchange('price_unit_uos')
    def onchange_price_unit_uos(self):
        coeff = 1
        if self.product_id and self.product_id.uos_coeff:
            coeff = self.product_id.uos_coeff
        self.price_unit = self.price_unit_uos * coeff

    price_unit_uos = fields.Float(
        'Unit Price UoS', digits_compute=dp.get_precision('Product Price'),
        readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
            name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(sale_order_line, self).product_id_change(
            pricelist=pricelist, product=product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position, flag=flag)
        if 'value' in res.keys() and 'price_unit' in res['value'].keys() and \
                'product_uos_qty' in res['value'].keys():
            prod_obj = self.env['product.product']
            prod = prod_obj.browse(product)
            res['value']['price_unit_uos'] = res[
                'value']['price_unit'] / prod.uos_coeff
        return res
