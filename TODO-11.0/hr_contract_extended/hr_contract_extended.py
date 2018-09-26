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
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrContractAcademicAchievement(models.Model):
    _name = 'hr.contract.academic.achievement'
    _description = 'Hr Contract Academic Achievement'
    
    degree_obtained=fields.Char('Degree Obtained', size=96, required=True)
    institution=fields.Char('Institution', size=64)
    date_obtained=fields.Date('Date Obtained')
    contract_academic_achievement=fields.Many2one('hr.contract', 'Academic Achievements')

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
        for salary_rule in self:
            if salary_rule.contract_id:
                salary_rule.contract_id.struct_id.write({'rule_ids':[(4, salary_rule.id)]})
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
    
    @api.depends('date_start','date_end')
    def _compute_duration(self):
        for contract in self:
            start_date = datetime.strptime(contract.date_start, "%Y-%m-%d")
            end_date = self._get_end_date(contract)
            
            self.duration_years= self._years_between(start_date, end_date)
            self.duration_months= self._months_between(start_date, end_date)
            self.duration_days= self._days_between(start_date, end_date)


    hr_salary_rule_ids=fields.One2many('hr.salary.rule', 'contract_id', 'Salary Rules')
    academic_achievement=fields.One2many('hr.contract.academic.achievement', 'contract_academic_achievement', 'Academic Achievements')
    duration_years= fields.Integer(compute="_compute_duration",string="Years", multi="sums")
    duration_months= fields.Integer(compute="_compute_duration",string="Months", multi="sums")
    duration_days= fields.Integer(compute="_compute_duration",string="Days", multi="sums")

    @api.multi
    def write(self,vals):
        payroll_struct_obj = self.env['hr.payroll.structure']
        if 'struct_id' in vals:
            for contract in self:
                if contract.hr_salary_rule_ids:
                    for salary_rule in contract.hr_salary_rule_ids: 
                        contract.struct_id.write({'rule_ids': [(3,salary_rule.id)]})
                        payroll_struct_obj.write(vals['struct_id'],{'rule_ids': [(4,salary_rule.id)]})
        return super(HrContract, self).write(vals)
    @api.multi
    def unlink(self):
        for contract in self:
            if contract.hr_salary_rule_ids:
                for salary_rule in contract.hr_salary_rule_ids: 
                    salary_rule.unlink()
        return super(HrContract, self).unlink()
