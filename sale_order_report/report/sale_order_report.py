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

import time
import pooler
from report import report_sxw
import locale

class sale_order_ccorp(report_sxw.rml_parse):

    def sale_order_ccorp_discount(self, sale_order):
        res = 0
        line_ids = self.pool.get('sale.order.line').search(self.cr, self.uid, [('order_id', '=', sale_order.id)])
        for line in line_ids:
            line_info = self.pool.get('sale.order.line').browse(self.cr, self.uid, line, self.context.copy())
            res += line_info.price_subtotal * line_info.discount / 100
        return res

    def __init__(self, cr, uid, name, context):
        super(sale_order_ccorp, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'discount': self.sale_order_ccorp_discount,
            'cr'  : cr,
            'uid' : uid,
        })
        self.context = context
        self._node = None

report_sxw.report_sxw(
    'report.sale.order.layout_ccorp',
    'sale.order',
    'addons/sale_order_ccorp_report/report/sale_order_report.mako',
    parser=sale_order_ccorp
)
