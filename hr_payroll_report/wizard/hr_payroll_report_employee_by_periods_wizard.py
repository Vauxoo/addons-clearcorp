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
from openerp.osv import fields,osv, orm
        
class ReportEmployeeByPeriodsWizard(osv.osv):

    _name = "report.employee.by.periods"
    _description = "Report Employee by Periods"
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',),
        'period_from': fields.many2one('account.period', 'Start Period',),
        'period_to': fields.many2one('account.period', 'End Period',),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }
            
    def _print_report(self, cursor, uid, ids, datas, context={}):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr_payroll_employee_by_periods_report',
            'datas': datas}

    def action_validate(self, cr, uid, ids, context={}):
        datas = {}
        datas['ids'] = context.get('active_ids', [])
        datas['model'] = context.get('active_model', 'ir.ui.menu')
        datas['form'] = self.read(cr, uid, ids, ['company_id',  'period_from', 'period_to'], context=context)[0]
        return self._print_report(cr, uid, ids, datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
