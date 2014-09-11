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

class SaleAdvancePayment(osv.TransientModel):

    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
        inv_id = super(SaleAdvancePayment, self)._create_invoices(cr, uid, inv_values, sale_id, context=context)
        order_obj = self.pool.get('sale.order')
        order = order_obj.browse(cr, uid, sale_id, context=context)
        if order.pricelist_id:
            inv_obj = self.pool.get('account.invoice')
            inv_obj.write(cr, uid, inv_id, {'pricelist_id': order.pricelist_id.id}, context=context)
        return inv_id