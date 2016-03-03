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
        # doc_ids = self
        res = self.read(cr, uid,
                        ids,
                        ['stock_location', 'product_ids'],
                        context=context
                        )
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id', False):
            datas['ids'] = [res['id']]
        return self.pool['report'].get_action(cr,
                                              uid, [],
                                              'stock_move_report.report_stock_move_order',
                                              data=datas, context=context)
