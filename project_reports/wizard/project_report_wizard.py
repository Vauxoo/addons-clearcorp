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

from osv import osv, fields

class Project(osv.osv):
    _inherit = "project.project"
    _columns = {
        'wizard_id' : fields.many2one('project.report.wizard', 'Wizard'),
    }

class ProjectWork(osv.osv):
    _inherit = "project.task.work"
    _columns = {
        'project': fields.related('task_id', 'project_id', type='many2one', relation='project.project', string='Project', store=False, readonly=True)
    }
    
class project_report_wizard (osv.osv):
    _name = 'project.report.wizard'
    _columns = {
        'date_from' : fields.date('Start Date', required=True),
        'date_to' : fields.date('End Date', required=True),
        'project_ids' : fields.one2many('project.project', 'wizard_id', 'Projects'),
    }
    
    
    def _print_report(self, cursor, uid, ids, datas, context=None):
        context = context or {}
       
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'project_report_report',
            'datas': datas}

    def action_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {}
        datas['ids'] = context.get('active_ids', [])
        datas['model'] = context.get('active_model', 'ir.ui.menu')
        datas['form'] = self.read(cr, uid, ids, ['date_from',  'date_to', 'project_ids'], context=context)[0]
        return self._print_report(cr, uid, ids, datas, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
