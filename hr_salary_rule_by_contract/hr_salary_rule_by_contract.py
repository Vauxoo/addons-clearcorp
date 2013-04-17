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
from osv import fields, osv

class HrSalaryRule(osv.osv):
    _inherit = 'hr.salary.rule'
    
    _columns = {
        'contract_id':fields.many2one('hr.contract', 'Contract'),
    }
    
    def satisfy_condition(self, cr, uid, rule_id, localdict, context=None):
        """
        @param rule_id: id of hr.salary.rule to be tested
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for the given contract. Return False otherwise.
        """
        rule = self.browse(cr, uid, [rule_id], context=context)[0]
        if 'contract' in localdict:
            contract = localdict['contract']
            if rule.contract_id and contract.id != rule.contract_id.id:
                return False
        
        result = super(HrSalaryRule, self).satisfy_condition(cr, uid, rule_id, localdict, context=context)
        return result

    def create(self, cr, uid, vals, context={}):
        res = super(HrSalaryRule, self).create(cr, uid, vals, context)
        structure_obj = self.pool.get('hr.payroll.structure')
        for salary_rule in self.browse(cr, uid, [res], context=context):
            if salary_rule.contract_id:
                structure_obj.write(cr, uid, [salary_rule.contract_id.struct_id.id], {'rule_ids':[(4, salary_rule.id)]}, context=context)
        return res

class HrContract(osv.osv):
    _inherit = 'hr.contract'
    
    _columns = {
        'hr_salary_rule_ids':fields.one2many('hr.salary.rule', 'contract_id', 'Salary Rules'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        salary_rule_obj = self.pool.get('hr.salary.rule')
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.hr_salary_rule_ids:
                for salary_rule in contract.hr_salary_rule_ids: 
                    salary_rule_obj.unlink(cr, uid, salary_rule.id, context)
        return super(HrContract, self).unlink(cr, uid, ids, context)
