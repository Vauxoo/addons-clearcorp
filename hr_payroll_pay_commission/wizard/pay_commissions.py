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

class PayCommissionsWizard(osv.TransientModel):
    """Commission Payroll Wizard"""

    _name = 'hr.payroll.pay.commission.pay.wizard'

    _description = __doc__

    def do_payment(self, cr, uid, ids, context=None):
        assert isinstance(ids,list)
        wizard = self.browse(cr, uid, ids[0], context=context)
        commission_obj = self.pool.get('sale.commission.commission')
        payment_obj = self.pool.get('hr.payslip.pay.commission.payment')
        input_obj = self.pool.get('hr.payslip.input')
        company_obj = self.pool.get('res.company')
        for slip in wizard.payslip_run_id.slip_ids:
            if not slip.employee_id.user_id:
                raise osv.except_osv(_('Error'), _('The employee %s does not have a user assigned') %
                    slip.employee_id.name)
            # Search all the users commissions
            user_id = slip.employee_id.user_id
            commission_ids = commission_obj.search(cr, uid, [('state','=','new'),
                ('user_id','=',user_id.id)], context=context)
            try:
                # Iterate all commissions of the user
                user_commissions = []
                total_commissions = 0.0
                # TODO: validate 0 amounts
                for commission in commission_obj.browse(cr, uid, commission_ids,
                context=context):
                    # Create the Payment
                    amount_paid = commission.residue
                    values = {
                        'commission_id': commission.id,
                        'input_id': False,
                        'amount_paid': amount_paid,
                    }
                    user_commissions.append(payment_obj.create(cr, uid, values, context=context))
                    total_commissions += amount_paid
                # Validate the contract
                if not slip.contract_id:
                    raise osv.except_osv(_('Error'), _('The slip for %s has no contract') %
                        slip.employee_id.name)
                # Create the input
                company = slip.employee_id.company_id
                if not company.pay_commission_name or \
                not company.pay_commission_code:
                    raise osv.except_osv(_('Error'),_('Commission parameters for company %s '
                    'are not set.') % company.name)
                values = {
                    'name': company.pay_commission_name,
                    'payslip_id': slip.id,
                    'sequence': company.pay_commission_sequence,
                    'code': company.pay_commission_code,
                    'amount': total_commissions,
                    'contract_id': slip.contract_id.id,
                }
                # TODO: validate 0 amounts
                input_id = input_obj.create(cr, uid, values, context=context)
                payment_obj.write(cr, uid, user_commissions, {'input_id': input_id}, context=context)
                slip.compute_sheet(context=context)
            except Exception as error:
                msg = _('An error occurred while executing the wizard. '
                        'The system error was :\n')
                for item in error.args:
                    msg += item + '\n'
                raise osv.except_osv(_('Error'), msg)
        return {
                'name': _('New Commissions'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hr.payslip.pay.commission.payment',
                'context': context,
                'type': 'ir.actions.act_window',
                'domain': [('id','in',user_commissions)]
                }

    _columns = {
        'payslip_run_id': fields.many2one('hr.payslip.run', string='Payslip Batch', required=True),
    }