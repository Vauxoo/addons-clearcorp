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

class Commission(osv.Model):

    _inherit = 'sale.commission.commission'

    def _compute_amounts(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        payment_obj = self.pool.get('hr.payroll.pay.commission.payment')
        for commission in self.browse(cr, uid, ids, context=context):
            payment_ids = payment_obj.search(cr, uid, [('commission_id','=',commission.id)], context=context)
            payments = payment_obj.browse(cr, uid, payment_ids, context=context)
            sum = reduce(lambda result,payment: result+payment.amount_paid, payments, 0.0)
            res[commission.id] = {
                'amount_paid': sum,
                'residue': commission.amount - sum,
            }
        return res

    _columns = {
        'amount_paid': fields.function(_compute_amounts, type='float', multi='amounts', string='Amount Paid'),
        'residue': fields.function(_compute_amounts, type='float', multi='amounts', string='Residue'),
    }