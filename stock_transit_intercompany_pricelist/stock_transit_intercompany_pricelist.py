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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp


class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def action_done(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.location_id.usage == 'transit':

                ir_property_obj = self.pool.get('ir.property')
                pricelist_obj = self.pool.get('product.pricelist')

                for quant in move.reserved_quant_ids:
                    quant.product_id.write({'intercompany_price': quant.cost})

                    price = pricelist_obj.price_get(cr, SUPERUSER_ID, [move.picking_id.partner_id.property_product_pricelist_purchase.id],
                            quant.product_id.id, quant.qty, move.company_id.partner_id.id, {
                                })[move.picking_id.partner_id.property_product_pricelist_purchase.id]
                    quant.write({'cost': price})

        return super(stock_move, self).action_done(cr, uid, ids, context=context)


class product_template(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
        'intercompany_price': fields.float('Intercompany Price', digits_compute=dp.get_precision('Product Price')),
    }
