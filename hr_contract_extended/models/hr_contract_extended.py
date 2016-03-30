# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrContractAcademicAchievement(models.Model):
    _name = 'hr.contract.academic.achievement'
    _description = 'Hr Contract Academic Achievement'

    degree_obtained = fields.Char('Degree Obtained', size=96, required=True)
    institution = fields.Char('Institution', size=64)
    date_obtained = fields.date('Date Obtained')
    contract_academic_achievement = fields.Many2one(
        'hr.contract', string='Academic Achievements')


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    contract_id = fields.Many2one('hr.contract', string='Contract')

    @api.model
    def satisfy_condition(self, rule_id, localdict):
        """
        @param rule_id: id of hr.salary.rule to be tested
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the
        given contract. Return False otherwise.
        """
        rule = self.browse(rule_id)
        if 'contract' in localdict:
            contract = localdict['contract']
            if rule.contract_id and contract.id != rule.contract_id.id:
                return False
        result = super(HrSalaryRule, self).satisfy_condition(rule_id,
                                                             localdict)
        return result

    @api.model
    def create(self, vals):
        res = super(HrSalaryRule, self).create(vals)
        structure_obj = self.pool.get('hr.payroll.structure')
        for salary_rule in self.browse(res):
            if salary_rule.contract_id:
                structure_obj.write([salary_rule.contract_id.struct_id.id],
                                    {'rule_ids': [(4, salary_rule.id)]})
        return res


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _get_end_date(self, contract):
        end_date = datetime.today()
        if contract.date_end and contract.date_end < str(end_date):
            end_date = datetime.strptime(contract.date_end, "%Y-%m-%d")
        return end_date

    def _days_between(self, start_date, end_date):
        return relativedelta(end_date, start_date).days

    def _months_between(self, start_date, end_date):
        return relativedelta(end_date, start_date).months

    def _years_between(self, start_date, end_date):
        return relativedelta(end_date, start_date).years

    @api.multi
    def _compute_duration(self, field_name, arg):
        res = {}
        for contract in self:
            start_date = datetime.strptime(contract.date_start, "%Y-%m-%d")
            end_date = self._get_end_date(contract)
            res[contract.id] = {
                'duration_years': self._years_between(start_date, end_date),
                'duration_months': self._months_between(start_date, end_date),
                'duration_days': self._days_between(start_date, end_date),
            }
        return res

    hr_salary_rule_ids = fields.One2many('hr.salary.rule', 'contract_id',
                                         string='Salary Rules'),
    academic_achievement = fields.One2many(
        'hr.contract.academic.achievement', 'contract_academic_achievement',
        'Academic Achievements')
    duration_years = fields.Integer(
        compute=_compute_duration, string="Years", multi="sums")
    duration_months = fields.Integer(
        compute=_compute_duration, string="Months", multi="sums")
    duration_days = fields.Integer(
        compute=_compute_duration, string="Days", multi="sums")

    @api.multi
    def write(self, vals):
        payroll_struct_obj = self.env['hr.payroll.structure']
        if 'struct_id' in vals:
            for contract in self:
                if contract.hr_salary_rule_ids:
                    for salary_rule in contract.hr_salary_rule_ids:
                        payroll_struct_obj.write(
                            contract.struct_id.id,
                            {'rule_ids': [(3, salary_rule.id)]})
                        payroll_struct_obj.write(
                            vals['struct_id'],
                            {'rule_ids': [(4, salary_rule.id)]})
        return super(HrContract, self).write(vals)

    @api.multi
    def unlink(self):
        salary_rule_obj = self.env['hr.salary.rule']
        for contract in self:
            if contract.hr_salary_rule_ids:
                for salary_rule in contract.hr_salary_rule_ids:
                    salary_rule_obj.unlink(salary_rule.id, )
        return super(HrContract, self).unlink(self._ids)
