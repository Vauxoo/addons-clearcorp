# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Addons modules by CLEARCORP S.A.
# Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_button_confirm(self):
        for sale_order in self:
            if not self.env['res.users'].has_group(
            'sale_order_restricted_availability.group_exceeding_limits_stock_sale'):
                for line in sale_order.order_line:
                    if line.product_id:
                        if line.product_id.type!='service' and (line.product_id.qty_available<line.product_uom_qty or line.product_id.qty_available<=0):
                            raise Warning(_('Not enough stock for product %s. Stock Actual: %s' %('['+line.product_id.default_code+']'+line.product_id.name,line.product_id.qty_available)))
        return super(SaleOrder,self).action_button_confirm()