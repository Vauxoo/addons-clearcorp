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

from openerp import models, api


class StockMove(models.Model):

    _inherit = 'stock.move'

    """@api.model
    def find_move_ancestors(self, move):
        if move.group_id:
            requisition_obj = self.env['purchase.requisition']
            requisitions = requisition_obj.search([
                ('state', '!=', 'cancel'),
                ('group_id', '=', move.group_id.id)])
            if requisitions:
                return True
        return super(StockMove, self).find_move_ancestors(move)"""

    @api.cr_uid_ids_context
    def do_unreserve(self, cr, uid, move_ids, context=None):
        super(StockMove, self).do_unreserve(
                cr, uid, move_ids, context=context)
        for move in self.browse(cr, uid, move_ids, context=context):
            if move.group_id:
                requisition_obj = self.pool.get('purchase.requisition')
                requisitions = requisition_obj.search(
                    cr, uid, [('state', '!=', 'cancel'),
                              ('group_id', '=', move.group_id.id)])
                if requisitions:
                    self.write(cr, uid, [move.id],
                               {'state': 'waiting'}, context=context)
