# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
import logging
from tools.translate import _

class sale_change_currency(osv.osv_memory):
    _name = 'sale.change.currency'
    _columns = {
       'pricelist_id': fields.many2one('product.pricelist', 'Change to', required=True, help="Seleccione un diario."),
    }

    def view_init(self, cr , uid , fields_list, context=None):
        obj_order = self.pool.get('sale.order')
        if context is None:
            context = {}
        if context.get('active_id',False):
            if obj_order.browse(cr, uid, context['active_id']).state != 'draft':
                raise osv.except_osv(_('Error'), _('You can only change currency for Draft Invoice !'))
            pass

    def change_currency(self, cr, uid, ids, context=None):

        for wiz in self.browse(cr, uid, ids, context=context):
            obj_order = self.pool.get('sale.order')
            obj_order_line = self.pool.get('sale.order.line')
            obj_pricelist = self.pool.get('product.pricelist')
            obj_currency = self.pool.get('res.currency')
            order = obj_order.browse(cr, uid, context['active_id'], context=context)


            data = {}
            if context is None:
                context = {}
            for obj in self.browse(cr, uid, ids, context=context):
                data = obj

            if data.pricelist_id.currency_id.id:
                new_currency = data.pricelist_id.currency_id.id
            else:
                new_currency = order.company_id.currency_id.id

            new_pricelist = data.pricelist_id
            old_pricelist = order.pricelist_id

            if order.pricelist_id.currency_id.id == new_currency:
                return {}

            while order.pricelist_id.currency_id.id != new_currency:
                order.write({'pricelist_id': new_pricelist.id},context=context)
                order = obj_order.browse(cr, uid, context['active_id'], context=context)

            rate = obj_currency.browse(cr, uid, new_currency, context=context).rate

            for line in order.order_line:

                new_price = line.price_unit * new_pricelist.currency_id.rate/ old_pricelist.currency_id.rate
                obj_order_line.write(cr, uid, [line.id], {'price_unit': new_price})

        return {'type': 'ir.actions.act_window_close'}

sale_change_currency()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
