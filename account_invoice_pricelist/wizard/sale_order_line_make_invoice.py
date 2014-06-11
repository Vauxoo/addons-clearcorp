# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Original Module by SIESA (<http://www.siesacr.com>)
#    Refactored by CLEARCORP S.A. (<http://clearcorp.co.cr>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import osv

class SaleOrderLineMakeInvoice(osv.TransientModel):

    _inherit = 'sale.order.line.make.invoice'

    def make_invoices(self, cr, uid, ids, context=None):
        res = super(SaleOrderLineMakeInvoice,self).make_invoices(cr, uid, ids, context=context)
        sale_order_line_obj = self.pool.get('sale.order.line')
        sale_order_ids = []
        for line in sale_order_line_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if line.order_id:
                sale_order_ids.append(line.order_id.id)
        sale_order_ids = list(set(sale_order_ids))
        if sale_order_ids:
            sale_order_obj = self.pool.get('sale.order')
            for sale_order_id in sale_order_ids:
                sale_order = sale_order_obj.browse(cr, uid, sale_order_id, context=context)
                if sale_order.pricelist_id:
                    for invoice in sale_order.invoice_ids:
                        invoice.write({'pricelist_id': sale_order.pricelist_id.id}, context=context)
        return res