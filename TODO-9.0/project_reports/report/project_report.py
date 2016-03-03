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
from openerp.report import report_sxw
from openerp import models
from openerp.tools.translate import _


class ProjectReportReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ProjectReportReport, self).__init__(cr, uid, name,
                                                  context=context)
        self.localcontext.update({
            'time': time,
            'report_name': _('Project Report'),
            'get_task_by_dates': self._get_task_by_dates,
            'get_projects': self._get_projects,
            'get_hours_projects': self._get_hours_projects,
        })

    def _get_task_by_dates(self, project_id, start_date, end_date):
        task_work_obj = self.pool.get('project.task.work')
        task_obj = self.pool.get('project.task')
        task_ids = task_obj.search(self.cr, self.uid, [('project_id', '=',
                                                        project_id)])
        task_work_ids = task_work_obj.search(self.cr,
                                             self.uid,
                                             [('date', '>=', start_date),
                                              ('date', '<=', end_date),
                                              ('task_id', 'in', task_ids)])
        task_ids = task_obj.search(self.cr, self.uid,
                                   [('project_id', '=', project_id),
                                    ('work_ids', 'in', task_work_ids)])
        tasks = task_obj.browse(self.cr, self.uid, task_ids)
        result = []
        for task in tasks:
            task_works = task_work_obj.search(self.cr, self.uid,
                                              [('task_id', '=', task.id),
                                               ('id', 'in', task_work_ids)])
            task_works = task_work_obj.browse(self.cr, self.uid, task_works)
            total_hours = 0.00
            for work in task_works:
                work_hours = round(work.hours, 2)
                total_hours += work_hours
            result.append((task, task_works, total_hours))
        return result

    def _get_hours_projects(self, project_ids, start_date, end_date):
        task_obj = self.pool.get('project.task')
        task_work_obj = self.pool.get('project.task.work')
        task_ids = task_obj.search(self.cr, self.uid,
                                   [('project_id', 'in', project_ids)])
        task_work_ids = task_work_obj.search(self.cr,
                                             self.uid,
                                             [('date', '>=', start_date),
                                              ('date', '<=', end_date),
                                              ('task_id', 'in', task_ids)])
        user_hours = {}
        total_hours = 0.00
        task_works = task_work_obj.browse(self.cr, self.uid, task_work_ids)
        for work in task_works:
            if work.user_id.id in user_hours:
                user_hours[work.user_id.id] = (work.user_id,
                                               user_hours[work.
                                                          user_id.
                                                          id][1] + work.hours
                                               )
                work_hours = round(work.hours, 2)
                total_hours += work_hours
            else:
                user_hours[work.user_id.id] = (work.user_id, work.hours)
                work_hours = round(work.hours, 2)
                total_hours += work_hours
        user_hours['total'] = total_hours
        return user_hours

    def get_project_tasks(self, cr, uid, project_task_works):
        project_tasks = []
        for project_task_work in project_task_works:
            if project_task_work.task_id not in project_tasks:
                project_tasks.append(project_task_work.task_id)
        return project_tasks

    def _get_projects(self, project_ids):
        return self.pool.get('project.project').browse(self.cr, self.uid,
                                                       project_ids)


class report_project_project(models.AbstractModel):
    _name = 'report.project_reports.report_project_project'
    _inherit = 'report.abstract_report'
    _template = 'project_reports.report_project_project'
    _wrapped_report_class = ProjectReportReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
