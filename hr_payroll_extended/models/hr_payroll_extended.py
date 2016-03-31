# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            help='Used to display the rule on reports'),
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
            _model, code_id = self.pool.get(
                'ir.model.data').get_object_reference(
                    cr, uid, 'hr_payroll_extended', 'data_input_value_1')
            input_value = self.pool.get(
                'hr.payroll.extended.input.value').browse(
                    cr, uid, code_id, context=context)
            for worked_days_line in day_lines:
                if worked_days_line['code'] == 'WORK100':
                    # Change it if there is no HN
                    if not has_hr:
                        worked_days_line['work_code'] = input_value.id
                        worked_days_line['code'] = input_value.code
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
                 'work_code': contract.fixed_working_hours_code.id,
                 'code': contract.fixed_working_hours_code.code,
                 'number_of_days': contract.fixed_working_days,
                 'number_of_hours': contract.fixed_working_hours,
                 'contract_id': contract.id,
            }
            res += [attendances]
        res += super(Payslip, self).get_worked_day_lines(
            cr, uid, contract_ids, date_from, date_to, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'period_id' in context:
            vals.update({'period_id': context.get('period_id')})
        return super(Payslip, self).create(cr, uid, vals, context=context)
