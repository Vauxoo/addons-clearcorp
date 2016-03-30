# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    contract_id = fields.Many2one('hr.contract', string='Contract')

    @api.Model
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
        res = super(HrSalaryRule, self).eate(vals)
        structure_obj = self.pool.get('hr.payroll.structure')
        for salary_rule in self.browse(res):
            if salary_rule.contract_id:
                structure_obj.write(salary_rule.contract_id.struct_id.id,
                                    {'rule_ids': [(4, salary_rule.id)]})
        return res


class HrContract(models.Model):
    _inherit = 'hr.contract'

    hr_salary_rule_ids = fields.One2many('hr.salary.rule', 'contract_id',
                                         string='Salary Rules')

    def unlink(self, ids, context=None):
        salary_rule_obj = self.pool.get('hr.salary.rule')
        for contract in self.browse(ids):
            if contract.hr_salary_rule_ids:
                for salary_rule in contract.hr_salary_rule_ids:
                    salary_rule_obj.unlink(salary_rule.id)
        return super(HrContract, self).unlink(ids)
