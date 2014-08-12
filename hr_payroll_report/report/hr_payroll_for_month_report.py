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

import pooler
from report import report_sxw
from tools.translate import _

class PayrollReportForMonth(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(PayrollReportForMonth, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.localcontext.update({
            'cr' : cr,
            'uid': uid,
            'get_period_by_id': self.get_period_by_id,
            'get_payslips_by_period': self.get_payslips_by_period,
            'get_payslips_by_struct': self.get_payslips_by_struct,
            'get_payslips_by_employee': self.get_payslips_by_employee,
            'get_identification': self.get_identification,
            'get_bank_account': self.get_bank_account,
            'get_hn': self.get_hn,
            'get_he': self.get_he,
            'get_basic': self.get_basic,
            'get_ext': self.get_ext,
            'get_gross': self.get_gross,
            'get_ccss': self.get_ccss,
            'get_bon': self.get_bon,
            'get_rent': self.get_rent,
            'get_net': self.get_net,
            'get_RETM':self.get_RETM,
            'get_RETS':self.get_RETS,
            'get_retroactive':self.get_retroactive,
        })
    def get_period_by_id(self, cr, uid, period_id):
        account_period_obj = self.pool.get('account.period')
        period = account_period_obj.browse(cr, uid, [period_id])[0]
        return period

    def get_payslips_by_period(self, cr, uid, start_period, stop_period):
        hr_payslip_object = self.pool.get('hr.payslip')
        payslips_ids = []
        payslips = []
            
        payslips_ids = hr_payslip_object.search(cr, uid, [('period_id.date_start', '>=' , start_period.date_start), ('period_id.date_stop', '<=' , stop_period.date_stop)])
        
        if len(payslips_ids) > 0:    
            payslips = hr_payslip_object.browse(cr, uid, payslips_ids)
        
        return payslips
        
    def get_payslips_by_struct(self, cr, uid, start_period, stop_period):
        all_payslips = self.get_payslips_by_period(cr, uid, start_period, stop_period)
        obj_by_struct = []
        struct_list = []
        payslip_by_struct = []

        for payslip in all_payslips:
            struct_name = payslip.struct_id.name
            if struct_name not in struct_list:
                struct_list.append(struct_name) 
                
        for struct in struct_list:
            struct_payslip = []
            for payslip in all_payslips:
                if payslip.struct_id.name == struct:
                    struct_payslip.append(payslip)
            obj_by_struct.append(struct_payslip)
                
        i = 0
        for struct in struct_list:
            tup_temp = (struct, obj_by_struct[i])
            payslip_by_struct.append(tup_temp)
            i += 1
            

        return payslip_by_struct
        
    def get_payslips_by_employee(self, cr, uid, all_payslips):
        obj_by_employee = []
        payslip_by_employee = []
        employee_list = []
        for payslip in all_payslips:
            employee_name = payslip.employee_id.name
            if employee_name not in employee_list:
                employee_list.append(employee_name)
            
        for employee in employee_list:
            employee_payslip = []
            for payslip in all_payslips:
                if payslip.employee_id.name == employee:
                    employee_payslip.append(payslip)
            obj_by_employee.append(employee_payslip)
                
        i = 0
        for employee in employee_list:
            tup_temp = (employee, obj_by_employee[i])
            payslip_by_employee.append(tup_temp)
            i += 1
                
        return payslip_by_employee
        
    def get_identification(self, cr, uid, payslips):
        res = ' '
        for payslip in payslips:
            res = payslip.employee_id.identification_id
            return res
            
    def get_bank_account(self, cr, uid, payslips):
        res = ' '
        for payslip in payslips:
            res = payslip.employee_id.bank_account_id.acc_number
            return res
        
    def get_hn(self, cr, uid, payslips):
        code = 'HN'
        res = 0.00
        for payslip in payslips:
            for line in payslip.worked_days_line_ids:
                if line.code == code:
                    res += line.number_of_hours
        return res
        
    def get_he(self, cr, uid, payslips):
        code = 'HE'
        res = 0.00
        for payslip in payslips:
            for line in payslip.worked_days_line_ids:
                if line.code == code:
                    res += line.number_of_hours        
        return res
    
    def get_basic(self, cr, uid, payslips):
        code = 'BASE'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == code:
                    res += line.total
        return res
        
    def get_ext(self, cr, uid, payslips):
        code = 'EXT'
        code2 = 'EXT-FE'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == code:
                    res += line.total
                elif line.code == code2:
                    res += line.total
                    
            res = res + self.get_retroactive(payslip.line_ids)
        return res
        
    def get_gross(self, cr, uid, payslips):
        code = 'BRUTO'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == code:
                    res += line.total
        return res
    
    def get_ccss(self, cr, uid, payslips):
        code = 'CCSS-EMP'
        code2 = 'CCSS-EMP-PEN'
        code3 = 'Banco Popular-EMP'
        code4 = 'CCSS-IVM'
        code5 = 'CCSS-SEM'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
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
    
    def get_bon(self, cr, uid, payslips):
        code = 'BON'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == code:
                    res += line.total
        return res
    
    def get_net(self, cr, uid, payslips):
        code = 'NETO'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
                if line.code == code:
                    res += line.total
        return res


    def get_rent(self, cr, uid, payslips):
        code = 'RENTA'
        res = 0.00
        for payslip in payslips:
            for line in payslip.line_ids:
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

report_sxw.report_sxw(
    'report.hr_payroll_report_for_month',
    'hr.payslip',
    'addons/hr_payroll_report/report/hr_payroll_report_for_month.mako',
    parser=PayrollReportForMonth)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
