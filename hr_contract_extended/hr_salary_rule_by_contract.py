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
from odoo import models, fields, api

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    contract_id=fields.Many2one('hr.contract', 'Contract')
    
    @api.multi
    def satisfy_condition(self,localdict):
        """
        @param rule_id: id of hr.salary.rule to be tested
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the given contract. Return False otherwise.
        """

        if 'contract' in localdict:
            contract = localdict['contract']
            if self.contract_id and contract.id != self.contract_id.id:
                return False
        
        result = super(HrSalaryRule, self).satisfy_condition(localdict)
        return result
    @api.model
    def create(self,vals):
        res = super(HrSalaryRule, self).create(vals)
        structure_obj = self.env['hr.payroll.structure']
        if res.contract_id:
            structure_obj.write([res.contract_id.struct_id.id], {'rule_ids':[(4, res.id)]})
        return res

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    hr_salary_rule_ids=fields.One2many('hr.salary.rule', 'contract_id', 'Salary Rules', change_default=True),
    
    @api.multi
    def unlink(self, cr, uid, ids, context=None):
        for contract in self:
            if contract.hr_salary_rule_ids:
                for salary_rule in contract.hr_salary_rule_ids: 
                    salary_rule.unlink()
        return super(HrContract, self).unlink()
