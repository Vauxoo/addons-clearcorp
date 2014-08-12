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

import time
import pooler
from report import report_sxw
import locale

class hrPaysliprunReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(hrPaysliprunReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr' : cr,
            'uid': uid,
            'get_hn':self.get_hn,
            'get_he':self.get_he,
            'get_fe':self.get_fe,
            'get_basic':self.get_basic,
            'get_ext':self.get_ext,
            'get_fes':self.get_fes,
            'get_gross':self.get_gross,
            'get_ccss':self.get_ccss,
            'get_net':self.get_net,
            'get_rent':self.get_rent,
            'get_obj_by_dep':self.get_obj_by_dep,
            'get_RETM':self.get_RETM,
            'get_RETS':self.get_RETS,
            'get_retroactive':self.get_retroactive,
            'get_bon': self.get_bon,
        })
    
    def get_prefix(self,currency,company_id):
        separator = ','
        decimal_point = '.'
        res = ''
        name_currency = currency.currency_name
        if name_currency == False:
            name_currency = company_id.currency_id.currency_name
            res = company_id.currency_id.symbol_prefix
        if name_currency == None:
            name_currency = company_id.currency_id.currency_name
            res = company_id.currency_id.symbol_prefix
        return res
        
    def get_hn(self,line_ids):
        code = 'HN'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.number_of_hours                
        return res
        
    def get_he(self,line_ids):
        code = 'HE'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.number_of_hours
        return res        
        
    def get_fe(self,line_ids):
        code = 'FE'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.number_of_hours        
        return res
    
    def get_basic(self,line_ids):
        code = 'BASE'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total        
        return res
        
    def get_ext(self,line_ids):
        code = 'EXT'
        code2 = 'EXT-FE'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
            elif line.code == code2:
                res += line.total
        
        res = res + self.get_retroactive(line_ids)
        return res
    
    
    def get_fes(self,line_ids):
        code = 'FES'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total        
        return res
        
        
    def get_gross(self,line_ids):
        code = 'BRUTO'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total        
        return res
    
    def get_ccss(self,line_ids):
        code = 'CCSS-EMP'
        code2 = 'CCSS-EMP-PEN'
        code3 = 'Banco Popular-EMP'
        code4 = 'CCSS-IVM'
        code5 = 'CCSS-SEM'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
            elif line.code == code2:
                res += line.total
            elif line.code == code3:
                res += line.total
            elif line.code == code4:
                res += line.total
            elif line.code == code5:
                res += line.total        
        return res    
    
    def get_net(self,line_ids):
        code = 'NETO'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
        return res

    def get_rent(self,line_ids):
        code = 'RENTA'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
        return res        
        
    def get_RETM(self,line_ids):
        code = 'RET-MENS'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
        return res

    def get_RETS(self,line_ids):
        code = 'RET-SEM'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
        return res
        
    def get_retroactive(self, line_ids):
        res = 0
        res = self.get_RETS(line_ids) + self.get_RETM(line_ids)
        return res

    def get_bon(self,line_ids):
        code = 'BON'
        res = 0
        for line in line_ids:
            if line.code == code:
                res += line.total
        return res

    def get_obj_by_dep(self,run):
        obj_by_dep = []
        dep_list = []
        emp_by_dep = []
    
        for payslip in run.slip_ids:
            dep_name = payslip.employee_id.department_id.name
            if dep_name not in dep_list:
                dep_list.append(dep_name)
    
        for dep in dep_list:
            dep_emp = []
            for payslip in run.slip_ids:
                if payslip.employee_id.department_id.name == dep:
                    dep_emp.append(payslip)
                obj_by_dep.append(dep_emp)
        i = 0
        for dep in dep_list:
            tup_temp = (dep, obj_by_dep[i])
            emp_by_dep.append(tup_temp)
            i += 1

        return emp_by_dep
    
        
report_sxw.report_sxw(
    'report.hr_payroll_payslip_run_report',
    'hr.payslip.run',
    'addons/cr_hr_report/report/hr_payroll_payslip_run_report.mako',
    parser=hrPaysliprunReport)
