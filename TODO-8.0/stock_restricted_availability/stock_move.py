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

from openerp.osv import osv, fields
from openerp.tools.translate import _

class StockMove(osv.Model):

    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.location_id.usage == 'internal' and \
            not move.location_id.allow_negative_moves:
                if not self.pool.get('res.users').has_group(cr, uid,
                'stock_restricted_availability.group_sale_unrestricted_availability'):
                    ctx = context.copy()
                    ctx.update({
                        'states': ('done',),
                        'what': ('in', 'out'),
                        'location': move.location_id.id,
                    })
                    qty = move.product_id.get_product_available(context=ctx)[move.product_id.id]
                    if qty - move.product_qty < 0.0:
                        raise osv.except_osv(_('Error validating the stock move'),_('There is not '
                        'enough product available to validate the stock move. Only authorized users '
                        'can validate this move.'))
        return super(StockMove, self).action_done(cr, uid, ids, context=context)

    def action_assign(self, cr, uid, ids, *args):
        for move in self.browse(cr, uid, ids):
            if move.location_id.usage == 'internal' and \
            not move.location_id.allow_negative_moves:
                if not self.pool.get('res.users').has_group(cr, uid,
                'stock_restricted_availability.group_sale_unrestricted_availability'):
                    ctx ={
                        'states': ('done',),
                        'what': ('in', 'out'),
                        'location': move.location_id.id,
                    }
                    qty = move.product_id.get_product_available(context=ctx)[move.product_id.id]
                    if qty - move.product_qty < 0.0:
                        raise osv.except_osv(_('Error validating the stock move'),_('There is not '
                        'enough product available to validate the stock move. Only authorized users '
                        'can validate this move.'))
        return super(StockMove, self).action_assign(cr, uid, ids, *args)

    def force_assign(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.location_id.usage == 'internal' and \
            not move.location_id.allow_negative_moves:
                if not self.pool.get('res.users').has_group(cr, uid,
                'stock_restricted_availability.group_sale_unrestricted_availability'):
                    ctx = context.copy()
                    ctx.update({
                        'states': ('done',),
                        'what': ('in', 'out'),
                        'location': move.location_id.id,
                    })
                    qty = move.product_id.get_product_available(context=ctx)[move.product_id.id]
                    if qty - move.product_qty < 0.0:
                        raise osv.except_osv(_('Error validating the stock move'),_('There is not '
                        'enough product available to validate the stock move. Only authorized users '
                        'can validate this move.'))
        return super(StockMove, self).force_assign(cr, uid, ids, context=context)