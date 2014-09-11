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
from openerp.tools.translate import _

class PaySlip(osv.Model):

    _inherit = 'hr.payslip'

    def compute_sheet(self, cr, uid, ids, context=None):
        payment_obj = self.pool.get('hr.payroll.pay.commission.payment')
        for slip in self.browse(cr, uid, ids, context=context):
            for input in slip.input_line_ids:
                if input.code == slip.employee_id.company_id.pay_commission_code:
                    total_commissions = 0.0
                    payment_ids = payment_obj.search(cr, uid, [('input_id','=',input.id)], context=context)
                    for payment in payment_obj.browse(cr, uid, payment_ids, context=context):
                        total_commissions += payment.amount_paid
                    if input.amount != total_commissions:
                        raise osv.except_osv(_('Error'),_('The total amount of commissions for %s '
                        'was modified from its original value %d') % (input.name, total_commissions))
        return super(PaySlip, self).compute_sheet(cr, uid, ids, context=context)
                    
    def process_sheet(self, cr, uid, ids, context=None):
        payment_obj = self.pool.get('hr.payroll.pay.commission.payment')
        for slip in self.browse(cr, uid, ids, context=context):
            payment_ids = payment_obj.search(cr, uid, [('slip_id','=',slip.id)], context=context)
            commission_ids = [elem['commission_id'] for elem in payment_obj.read(cr, uid, payment_ids,
                fields=['commission_id'], context=context)]
            commission_ids = list(set(commission_ids))
            for commission in self.browse(cr, uid, commission_ids, context=context):
                try:
                    if commission.invoice_id.state == 'paid':
                        if commission.amount_paid >= commission.amount:
                            commission.write({'state': 'paid'}, context=context)
                            commission.invoice_id.write({'commission_payment_complete': True},
                                context=context)
                except:
                    osv.except_osv(_('Error'),_('An error occurred while validating the Payslip.'))
        return super(PaySlip, self).process_sheet(cr, uid, ids, context=context)