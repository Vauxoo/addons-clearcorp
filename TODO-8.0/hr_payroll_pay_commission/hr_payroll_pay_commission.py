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

class Payment(osv.Model):
    """Commissions Payroll Payment"""

    _name = 'hr.payroll.pay.commission.payment'

    _description = __doc__

    def _check_amount_paid(self, cr, uid, ids, context=None):
        for payment in self.browse(cr, uid, ids, context=context):
            if payment.amount_paid <= 0.0:
                return False
        return True

    _columns = {
        'commission_id': fields.many2one('sale.commission.commission', string='Commission'),
        'invoice_id': fields.related('commission_id', 'invoice_id', type='many2one',
            obj='account.invoice', string='Invoice', readonly=True),
        'input_id': fields.many2one('hr.payslip.input', ondelete='restrict', string='Input'),
        'slip_id':fields.related('input_id', 'payslip_id', type='many2one',
            string='Payslip', obj='hr.payslip', readonly=True, store=True),
        'amount_paid': fields.float('Amount Paid', digits=(16,2)),
    }

    _constraints = [(_check_amount_paid, 'Value must be greater or equal than 0.', ['amount_paid'])]