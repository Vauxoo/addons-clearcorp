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

class project_project (osv.Model):
    
    def _search_related_issues(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        issue_ids = self.pool.get('project.issue').search(cr, uid, [('project_id', 'in', ids)])
        for issue in self.pool.get('project.issue').browse(cr, uid, issue_ids, context):
            if issue.state not in ('done', 'cancelled'):
                res[issue.project_id.id] += 1
        return res
    
    def _search_related_tasks(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        task_ids = self.pool.get('project.task').search(cr, uid, [('project_id', 'in', ids)])
        for task in self.pool.get('project.task').browse(cr, uid, task_ids, context):
            if task.state not in ('done', 'cancelled'):
                res[task.project_id.id] += 1
        return res
    
    _inherit = 'project.project'
    
    _columns = {
                'related_issues': fields.function(_search_related_issues, type='integer', store=True),
                'related_tasks': fields.function(_search_related_tasks, type='integer', store=True),
                }