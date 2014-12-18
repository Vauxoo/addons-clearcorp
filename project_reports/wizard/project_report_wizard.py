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

from openerp.osv import osv, fields

class project_report_wizard (osv.TransientModel):
    _name = 'project.report.wizard'
    _columns = {
        'date_from' : fields.date('Start Date', required=True),
        'date_to' : fields.date('End Date', required=True),
        'project_ids' : fields.many2many('project.project', string='Projects'),
    }

    def print_report(self, cr, uid, ids, datas, context=None):
        context = context or {}
        wizard = self.browse(cr, uid, ids[0],context=context)
        if wizard.project_ids:
            project_ids = [project.id for project in wizard.project_ids]
        else:
            project_ids = self.pool.get('project.project').search(
                cr, uid, [('use_tasks','=',True)],context=context)
        data = {
            'form': {
                'date_from': wizard.date_from,
                'date_to': wizard.date_to,
            }
        }
        res = self.pool.get('report').get_action(cr, uid, project_ids,
            'project_reports.report_project_project', data=data, context=context)
        return res

        """return {
            'type': 'ir.actions.report.xml',
            'report_name': 'project_report_report',
            'datas': datas}"""

    """def action_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {}
        datas['ids'] = context.get('active_ids', [])
        datas['model'] = context.get('active_model', 'ir.ui.menu')
        datas['form'] = self.read(cr, uid, ids, ['date_from',  'date_to', 'project_ids'], context=context)[0]
        return self._print_report(cr, uid, ids, datas, context=context)"""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
