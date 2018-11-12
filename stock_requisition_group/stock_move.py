# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, api


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

"""
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
"""
