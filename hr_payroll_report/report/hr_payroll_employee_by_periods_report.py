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

class ReportEmployeeByPeriods(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReportEmployeeByPeriods, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.localcontext.update({
            'cr' : cr,
            'uid': uid,
            'get_period_by_id': self.get_period_by_id,
            'get_payslips_by_employee': self.get_payslips_by_employee,
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
        
    def get_payslips_by_employee(self, cr, uid, start_period, stop_period):
        hr_payslip_object = self.pool.get('hr.payslip')
        payslips_ids = []
        payslips = []
            
        payslips_ids = hr_payslip_object.search(cr, uid, [('period_id.date_start', '>=' , start_period.date_start), ('period_id.date_stop', '<=' , stop_period.date_stop), ('employee_id.user_id', '<=' , uid)])
        
        if len(payslips_ids) > 0:    
            payslips = hr_payslip_object.browse(cr, uid, payslips_ids)
        
        return payslips
        
    def get_hn(self, cr, uid, payslip):
        code = 'HN'
        res = 0.00
        for line in payslip.worked_days_line_ids:
            if line.code == code:
                res += line.number_of_hours
        return res
        
    def get_he(self, cr, uid, payslip):
        code = 'HE'
        res = 0.00
        for line in payslip.worked_days_line_ids:
            if line.code == code:
                res += line.number_of_hours        
        return res
    
    def get_basic(self, cr, uid, payslip):
        code = 'BASE'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
        
    def get_ext(self, cr, uid, payslip):
        code = 'EXT'
        code2 = 'EXT-FE'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
            elif line.code == code2:
                res += line.total
        res = res + self.get_retroactive(payslip)
        return res
        
    def get_gross(self, cr, uid, payslip):
        code = 'BRUTO'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
    
    def get_ccss(self, cr, uid, payslip):
        code = 'CCSS-EMP'
        code2 = 'CCSS-EMP-PEN'
        code3 = 'Banco Popular-EMP'
        code4 = 'CCSS-IVM'
        code5 = 'CCSS-SEM'
        res = 0.00
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
    
    def get_bon(self, cr, uid, payslip):
        code = 'BON'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
    
    def get_net(self, cr, uid, payslip):
        code = 'NETO'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res


    def get_rent(self, cr, uid, payslip):
        code = 'RENTA'
        res = 0.00
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
    
    def get_RETM(self,payslip):
        code = 'RET-MENS'
        res = 0
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res

    def get_RETS(self,payslip):
        code = 'RET-SEM'
        res = 0
        for line in payslip.line_ids:
            if line.code == code:
                res += line.total
        return res
        
    def get_retroactive(self, payslip):
        res = 0
        res = self.get_RETS(payslip) + self.get_RETM(payslip)
        return res

report_sxw.report_sxw(
    'report.hr_payroll_employee_by_periods_report',
    'hr.payslip',
    'addons/hr_payroll_report/report/hr_payroll_employee_by_periods_report.mako',
    parser=ReportEmployeeByPeriods)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
