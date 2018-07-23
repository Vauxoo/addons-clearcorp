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

from odoo import tools,models, fields, api,_
from datetime import datetime
from openerp.tools.translate import _
from odoo.exceptions import UserError


class Company(models.Model):

    _inherit = 'res.company'

    payslip_footer= fields.Text(string='Payslip footer')


class SalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    appears_on_report= fields.Boolean(
            string='Appears on Report',
            help='Used to display the rule on reports',default=True)

class Job(models.Model):
    _inherit = 'hr.job'

    code= fields.Char(string='Code', size=128, required=False)


class PayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    date = fields.Date(string='Date Force', states={'draft': [('readonly', False)]})
    schedule_pay= fields.Selection([
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], string='Scheduled Pay', index=True, readonly=True,
            states={'draft': [('readonly', False)]})

    def close_payslip_run(self):
        result = self.write({'state': 'close'})
        payslip_obj = self.env['hr.payslip']
        for batches in self:
            payslip_ids = map(lambda x: x.id, batches.slip_ids)
            for payslip in payslip_obj.browse(payslip_ids):
                    if payslip.state == 'draft':
                        raise UserError(_('You did not confirm a payslip'))
                        break
        return result

    def confirm_payslips(self):
        payslip_obj = self.env['hr.payslip']
        for batches in self:
            payslip_ids = map(lambda x: x.id, batches.slip_ids)
            for payslip in payslip_obj.browse(payslip_ids):
                    if payslip.state == 'draft':
                        payslip.action_payslip_done()
        return True

    def compute_payslips(self):
        payslip_obj = self.env['hr.payslip']
        for batches in self:
            payslip_ids = map(lambda x: x.id, batches.slip_ids)
            for payslip in payslip_obj.browse(payslip_ids):
                if payslip.state == 'draft':
                    payslip.compute_sheet()
        return True


class Payslip(models.Model):

    _inherit = 'hr.payslip'

    name=fields.Char(
            string='Description', size=256, required=False,
            readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    def onchange_employee_id(self,date_from,date_to,employee_id,contract_id):
        res = super(Payslip, self).onchange_employee_id(date_from,date_to,employee_id,contract_id)
        contract = []
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']

        employee = employee_obj.browse(employee_id)

        if (not contract_id):
            contract_id = contract_obj.search([('employee_id', '=', employee_id)])
        else:
            contract_id = [contract_id]

        contracts = contract_obj.browse(contract_id)
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
            _model, code_id = self.env['ir.model.data'].get_object_reference('hr_payroll_extended', 'data_input_value_1')
            input_value = self.env['hr.payroll.extended.input.value'].browse(code_id)
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
    def get_worked_day_lines(self,contract_ids,date_from, date_to):
        res = []
        for contract in self.env['hr.contract'].browse(contract_ids):
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
        res += super(Payslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
        return res
    @api.model
    def create(self,vals):
        if 'date' in self._context:
            vals.update({'date': self._context.get('date')})
        return super(Payslip, self).create(vals)
