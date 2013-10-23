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
import time
from report import report_sxw
from tools.translate import _

class project_report_report(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(project_report_report, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        self.localcontext.update({
            'time': time,
            'cr' : cr,
            'uid': uid,
            'report_name':_('Project Report'),
            'get_project_task_works_by_dates': self.get_project_task_works_by_dates,
            'get_project_tasks': self.get_project_tasks,
            'get_projects': self.get_projects,
            'get_user_hours': self.get_user_hours,
        })
        
    def get_project_task_works_by_dates(self, cr, uid, start_date, end_date, project_ids=[]):
        project_task_work_obj = self.pool.get('project.task.work')
        
        project_task_work_ids = []
        if project_ids == []:
            project_task_work_ids = project_task_work_obj.search(cr, uid, [('date','>=',start_date), ('date','<=',end_date)])
        else:
            project_task_work_ids = project_task_work_obj.search(cr, uid, [('date','>=',start_date), ('date','<=',end_date), ('project', 'in', project_ids)])
        
        project_task_works = project_task_work_obj.browse(cr, uid, project_task_work_ids)
        return project_task_works
        
    def get_project_tasks(self, cr, uid, project_task_works):
        project_tasks = []
        for project_task_work in project_task_works:
            if project_task_work.task_id not in project_tasks:
                project_tasks.append(project_task_work.task_id)        
        return project_tasks
        
    def get_projects(self, cr, uid, project_tasks):
        projects = []
        for project_task in project_tasks:
            if project_task.project_id and project_task.project_id not in projects:
                projects.append(project_task.project_id)
        return projects
        
    def get_user_hours(self, cr, uid, project_task_works):
        user_hours = {}
        for project_task_work in project_task_works:
            if project_task_work.user_id.name not in user_hours and project_task_work.task_id.project_id:
                user_hours[project_task_work.user_id.name] = 0.00
        return user_hours
    

report_sxw.report_sxw('report.project_report_report', 
        'project.project',
        'addons/project_reports/report/project_report.mako',
        parser=project_report_report, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
