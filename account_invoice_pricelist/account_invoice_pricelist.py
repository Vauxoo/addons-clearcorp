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

from openerp.osv import osv, fields

class Invoice(osv.Model):

    _inherit = 'account.invoice'

    _columns = {
        'pricelist_id': fields.many2one('product.pricelist', string='Pricelist'),
    }

class StockPicking(osv.Model):

    _inherit = 'stock.picking'

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        invoice_obj = self.pool.get('account.invoice')
        if picking.purchase_id:
            if picking.purchase_id.pricelist_id:
                invoice_obj.write(cr, uid, invoice_id, {'pricelist_id': picking.purchase_id.pricelist_id.id})
        elif picking.sale_id:
            if picking.sale_id.pricelist_id:
                invoice_obj.write(cr, uid, invoice_id, {'pricelist_id': picking.sale_id.pricelist_id.id})
        return super(StockPicking, self)._invoice_hook(cr, uid, picking, invoice_id)

class PurchaseOrder(osv.Model):

    _inherit = 'purchase.order'

    def view_invoice(self, cr, uid, ids, context=None):
        res = super(PurchaseOrder, self).view_invoice(cr, uid, ids, context=context)
        for po in self.browse(cr, uid, ids, context=context):
            for invoice in po.invoice_ids:
                invoice.write({'pricelist_id': po.pricelist_id.id}, context=context)
        return res

class SaleOrder(osv.Model):

    _inherit = 'sale.order'

    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_id = super(SaleOrder, self)._make_invoice(cr, uid, order, lines, context=context)
        if order.pricelist_id:
            invoice_obj = self.pool.get('account.invoice')
            invoice_obj.write(cr, uid, inv_id, {'pricelist_id': order.pricelist_id.id}, context=context)
        return inv_id