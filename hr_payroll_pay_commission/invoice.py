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

    def _compute_commission_payments(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        payment_obj = self.pool.get('hr.payslip.pay.commission.payment')
        for invoice in self.browse(cr, uid, ids, context=context):
            payment_ids = payment_obj.search(cr, uid, [('invoice_id','=',invoice.id)], context=context)
            res[invoice.id] = payment_ids
        return res

    _columns = {
        'commission_payment_ids': fields.function(_compute_commission_payments, type='one2many',
            obj='hr.payslip.pay.commission.payment', string='Commission Payments'),
        'commission_payment_complete': fields.boolean('Commission Payment Complete'),
    }