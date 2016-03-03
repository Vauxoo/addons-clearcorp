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

                    res_id = 'res.partner,'+str(move.company_id.partner_id.id) # Costa Rica
                    ctx = context.copy()
                    ctx['force_company'] = quant.company_id.id
                    domain = ir_property_obj._get_domain(cr, uid, 'property_product_pricelist', 'res.partner', context=ctx)
                    if domain is None:
                        raise osv.except_osv(_('Error'),_('There is no property defined for Sale Pricelist'))

                    domain = ['|',('res_id', '=', res_id),('res_id','=',False)] + domain
                    #make the search with company_id asc to make sure that properties specific to a company are given first
                    nid = ir_property_obj.search(cr, SUPERUSER_ID, domain, limit=1, order='company_id asc, res_id asc', context=context)
                    if not nid:
                        raise osv.except_osv(_('Error'),_('There is not pricelist available for partner %s') % move.company_id.partner_id)

                    record = ir_property_obj.browse(cr, SUPERUSER_ID, nid[0], context=context)
                    pricelist = ir_property_obj.get_by_record(cr, SUPERUSER_ID, record, context=context)

                    price = pricelist_obj.price_get(cr, SUPERUSER_ID, [pricelist.id],
                            quant.product_id.id, quant.qty, move.company_id.partner_id.id, {
                                })[pricelist.id]
                    quant.write({'cost': price})

        return super(stock_move, self).action_done(cr, uid, ids, context=context)


class product_template(osv.osv):
    _inherit = 'product.template'
    
    _columns = {
        'intercompany_price': fields.float('Intercompany Price', digits_compute=dp.get_precision('Product Price')),
    }
