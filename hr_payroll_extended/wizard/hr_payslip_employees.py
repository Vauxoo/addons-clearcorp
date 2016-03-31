# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv


class hr_payslip_employees(osv.osv_memory):

    _inherit = 'hr.payslip.employees'

    def compute_sheet(self, cr, uid, ids, context=None):
        run_pool = self.pool.get('hr.payslip.run')
        if context is None:
            context = {}
        if context.get('active_id'):
            run_data = run_pool.read(cr, uid, context['active_id'],
                                     ['period_id'])
        period_id = run_data.get('period_id')
        period_id = period_id and period_id[0] or False
        if period_id:
            context = dict(context, period_id=period_id)
        return super(hr_payslip_employees, self).compute_sheet(cr, uid, ids,
                                                               context=context)
