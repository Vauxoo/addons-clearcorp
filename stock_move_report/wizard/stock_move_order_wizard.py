# -*- coding: utf-8 -*-
# © 2015 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class ReportStockMoveOrder(osv.osv_memory):

    _name = 'report.stock.move.order.wiz'

    _columns = {
        'stock_location': fields.many2one('stock.location',
                                          string='Stock Location'),
        'product_ids': fields.many2many('product.product',
                                        string='Product',
                                        domain=[('type', '=', 'product')]),
            }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid,
                        ids,
                        ['stock_location', 'product_ids'],
                        context=context
                        )
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id', False):
            datas['ids'] = [res['id']]
        return self.pool['report'].get_action(
            cr, uid, [], 'stock_move_report.report_stock_move_order',
            data=datas, context=context)
