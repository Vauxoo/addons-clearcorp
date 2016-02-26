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


class product_template(models.Model):
    _inherit = "product.template"


    @api.onchange('list_price_uos','uos_coeff')
    def onchange_list_price_uos(self):
        if self.uos_coeff == 0:
            self.uos_coeff = 1
        self.list_price = self.list_price_uos * self.uos_coeff
    
    list_price_uos = fields.Float('Sale Price UoS',digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price by UoS")
    
    @api.constrains('uos_coeff')
    def check_uos_coeff(self): # function for verify the field uos_coeff  is not negative
        if self.uos_coeff < 0:
            raise Warning (_('The camp Unit of Measure -> UOS Coeff can not be negative'))
        