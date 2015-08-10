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

from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _


class Company(osv.Model):

    _inherit = 'res.company'

    _columns = {
        'payslip_footer': fields.text('Payslip footer'),
    }


class SalaryRule(osv.Model):

    _inherit = 'hr.salary.rule'

    _columns = {
        'appears_on_report': fields.boolean(
            'Appears on Report',
            help='Used to display of rule on payslip reports'),
    }

    _defaults = {
        'appears_on_report': True,
    }


class Job(osv.Model):

    _inherit = 'hr.job'

    _columns = {
        'code': fields.char('Code', size=128, required=False),
    }


class PayslipRun(osv.Model):

    _inherit = 'hr.payslip.run'

    _columns = {
        'period_id': fields.many2one(
            'account.period', 'Force Period',
            readonly=True, states={'draft': [('readonly', False)]}),
        'schedule_pay': fields.selection([
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', select=True, readonly=True,
            states={'draft': [('readonly', False)]}),
    }

    def close_payslip_run(self, cr, uid, ids, context=None):
        result = self.write(cr, uid, ids, {'state': 'close'}, context=context)
        payslip_obj = self.pool.get('hr.payslip')
        for batches in self.browse(cr, uid, ids, context=context):
            payslip_ids = map(lambda x: x.id, batches.slip_ids)
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                    if payslip.state == 'draft':
                        raise osv.except_osv(
                            _('Warning !'),
                            _('You did not confirm a payslip'))
                        break
        return result

    def confirm_payslips(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        for batches in self.browse(cr, uid, ids, context=context):
            payslip_ids = map(lambda x: x.id, batches.slip_ids)
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                    if payslip.state == 'draft':
                        payslip_obj.compute_sheet(
                            cr, uid, [payslip.id], context=context)
                        payslip_obj.process_sheet(
                            cr, uid, [payslip.id], context=context)
        return True

    def compute_payslips(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        for batches in self.browse(cr, uid, ids, context=context):
            payslip_ids = map(lambda x: x.id, batches.slip_ids)
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                if payslip.state == 'draft':
                    payslip_obj.compute_sheet(
                        cr, uid, [payslip.id], context=context)
        return True


class Payslip(osv.osv):

    _inherit = 'hr.payslip'

    _columns = {
        'name': fields.char(
            'Description', size=256, required=False,
            readonly=True, states={'draft': [('readonly', False)]}),
        'forced_period_id': fields.related(
            'payslip_run_id', 'period_id',
            type="many2one", relation="account.period",
            string="Force period", store=True, readonly=True),
    }

    def onchange_employee_id(
            self, cr, uid, ids, date_from, date_to,
            employee_id=False, contract_id=False, context=None):

        res = super(Payslip, self).onchange_employee_id(
            cr, uid, ids, date_from, date_to, employee_id=employee_id,
            contract_id=contract_id, context=context)

        contract = []

        if (not employee_id) or (not date_from) or (not date_to):
            return res

        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')

        employee = employee_obj.browse(cr, uid, employee_id, context=context)

        if (not contract_id):
            contract_id = contract_obj.search(
                cr, uid, [('employee_id', '=', employee_id)], context=context)
        else:
            contract_id = [contract_id]

        contracts = contract_obj.browse(cr, uid, contract_id, context=context)
        if len(contracts) > 0 and len(contracts) >= 2:
            contract = contracts[0]
        schedule_pay = ''
        if contract and contract.schedule_pay:
            # This is to translate the terms
            if contract.schedule_pay == 'weekly':
                schedule_pay = _('weekly')
            elif contract.schedule_pay == 'monthly':
                schedule_pay = _('monthly')

        # Format dates
        date_from_payslip = datetime.strptime(date_from, "%Y-%m-%d")
        date_from_payslip = date_from_payslip.strftime('%d-%m-%Y')
        date_to_payslip = datetime.strptime(date_to, "%Y-%m-%d")
        date_to_payslip = date_to_payslip.strftime('%d-%m-%Y')

        name = _('%s payroll of %s from %s to %s') % (
            schedule_pay, employee.name, date_from_payslip, date_to_payslip)
        name = name.upper()
        worked_days_line_list = []
        if res['value']['worked_days_line_ids']:
            day_lines = res['value']['worked_days_line_ids']
            # Check if there is an element with code HR
            has_hr = False
            for worked_days_line in day_lines:
                if worked_days_line['code'] == 'HR':
                    has_hr = True
            # Change lines where code == WORK100
            for worked_days_line in day_lines:
                if worked_days_line['code'] == 'WORK100':
                    # Change it if there is no HN
                    if not has_hr:
                        worked_days_line['code'] = 'HN'
                        worked_days_line['name'] = name
                    # Ignore it if there is another HN line
                    else:
                        continue
                worked_days_line_list.append(worked_days_line)

        res['value'].update({
                    'name': name,
                    'worked_days_line_ids': worked_days_line_list,
        })
        return res

    def get_worked_day_lines(
            self, cr, uid, contract_ids,
            date_from, date_to, context=None):
        res = []
        for contract in self.pool.get('hr.contract').browse(
                cr, uid, contract_ids, context=context):
            # Check if the contract uses fixed working hours
            if not contract.use_fixed_working_hours:
                continue
            attendances = {
                 'name': _("Worked Hours"),
                 'sequence': 1,
                 'code': contract.fixed_working_hours_code,
                 'number_of_days': contract.fixed_working_hours,
                 'number_of_hours': contract.fixed_working_days,
                 'contract_id': contract.id,
            }
            res += [attendances]
        res += super(Payslip, self).get_worked_day_lines(
            cr, uid, contract_ids, date_from, date_to, context=context)
        return res

    def process_sheet(self, cr, uid, ids, context=None):
        res = super(Payslip, self).process_sheet(cr, uid, ids, context=context)
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        for payslip in self.browse(cr, uid, ids, context=context):
            if payslip.forced_period_id:
                self.write(
                    cr, uid, [payslip.id],
                    {'period_id': payslip.forced_period_id.id},
                    context=context)
                account_move_obj.write(
                    cr, uid, [payslip.move_id.id],
                    {'period_id': payslip.forced_period_id.id},
                    context=context)
                for line in payslip.move_id.line_id:
                    account_move_line_obj.write(
                        cr, uid, line.id,
                        {'period_id': payslip.forced_period_id.id},
                        context=context)
        return res
