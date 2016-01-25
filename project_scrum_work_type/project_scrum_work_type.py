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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class FeatureHours(osv.Model):
    
    _name = 'project.scrum.feature.hours'
   
   
    def _effective_hours(self, cr , uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid, [('feature_id', '=', hour.feature_id.id)], context=context)
            tasks = task_obj.browse(cr, uid, task_ids, context=context)
            sum = 0.0
            for task in tasks:
                if task.work_type_id == hour.work_type_id:
                    sum += task.effective_hours
            res[hour.id] = sum
        return res
    
    def _remaining_hours(self, cr , uid, ids, field_name, arg, context=None):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = task.expected_hours - task.effective_hours
        return res


    
    _columns = {
                'feature_id': fields.many2one('project.scrum.feature', string='Feature', required=True,
                    ondelete='cascade'),
                'work_type_id': fields.many2one('project.work.type', string='Work Type'),
                'expected_hours': fields.float('Planned Hour(s)', required=True),
                'effective_hours': fields.function(_effective_hours, type='float', string='Spent Hour(s)', store=True),
                'remaining_hours': fields.function(_remaining_hours, type='float', string='Remaining Hour(s)', store=True),
                }
    
    _defaults = {
                 'feature_id': lambda slf, cr, uid, ctx: ctx.get('feature_id', False),
                 }
    
class Feature(osv.Model):
    
    _inherit = 'project.scrum.feature'
    
    _columns = {
                'hour_ids': fields.one2many('project.scrum.feature.hours', 'feature_id', string='Feature Hours'),
                }
    
    def create_tasks(self, cr, uid, context):
        active_ids = context.get('active_ids', [])
        feature_obj = self.pool.get('project.scrum.feature')
        for feature in feature_obj.browse(cr, uid, active_ids, context=context):
            for feature_hour in feature.hour_ids:
                try:
                    values = {
                                  'name': feature.code + ' ' + feature.name,
                                  'project_id': feature.project_id.id,
                                  'work_type_id': feature_hour.work_type_id.id,
                                  'sprint_id': False,
                                  'feature_id': feature.id,
                                  'description': feature.description,
                                  'planned_hours': feature_hour.expected_hours,
                                  'date_deadline': feature.deadline,
                                  'date_start': feature.date_start,
                                  'is_scrum': True,
                                  }
                    task_obj = self.pool.get('project.task')
                    task_id = task_obj.create(cr, uid, values, context=context)
                except:
                    raise osv.except_osv(_('Error'), _('An error occurred while creating the tasks. '
                                                      'Please contact your system administrator.'))
               
           
    def write(self, cr, uid, ids, values, context=None):
        if 'hour_ids' in values:
            hours = values['hour_ids']
            sum = 0.0
            for hour in hours:
                id = hour[1]
                vals = hour[2]
                if vals: 
                    if 'expected_hours' in vals:
                        sum += vals['expected_hours']
                else:
                    hour_obj = self.pool.get('project.scrum.feature.hours')
                    sum += hour_obj.browse(cr, uid, id, context=context).expected_hours
            values['expected_hours'] = sum
        return super(Feature, self).write(cr, uid, ids, values, context=context)
    
    def create(self, cr, uid, values, context=None):
        if 'hour_ids' in values:
            hours = values['hour_ids']
            sum = 0.0
            for hour in hours:
                id = hour[1]
                vals = hour[2]
                if vals: 
                    if 'expected_hours' in vals:
                        sum += vals['expected_hours']
                else:
                    hour_obj = self.pool.get('project.scrum.feature.hours')
                    sum += hour_obj.browse(cr, uid, id, context=context).expected_hours
            values['expected_hours'] = sum
        return super(Feature, self).create(cr, uid, values, context=context)

class Task(osv.Model):
    
    _inherit = 'project.task'

    def onchange_sprint(self, cr, uid, ids, sprint_id, context=None):
       res = {}
       return res

    def _remaining_hours(self, cr , uid, ids, field_name, arg, context=None):
        res = {}
        effective_hours = 0
        for task in self.browse(cr, uid, ids, context=context):
            for work in task.work_ids:
                effective_hours = effective_hours + work.hours
            remaining = task.planned_hours - effective_hours + task.reassignment_hour
            res[task.id] = remaining
        return res

    def _validate_planned_hours(self, cr, uid, ids, context=None):
        for task in self.browse(cr, uid, ids, context):
            if task.planned_hours == 0.0:
                return False
            else:
                return True

    _columns = {
                'feature_hour_ids': fields.related('feature_id', 'hour_ids', type='one2many',
                    relation='project.scrum.feature.hours', string='Feature Hours', readonly=True),
                'remaining_hours': fields.function(_remaining_hours, type='float', string='Remaining Hour(s)', store=True),
                }
    _constraints = [
        (_validate_planned_hours, 'Planned hours can\'t be zero',
         ['planned_hours'])
    ]


    def create(self, cr, uid, values, context=None):
        if 'project_id' in values:
            project_obj = self.pool.get('project.project')
            project = project_obj.browse(cr, uid, values['project_id'], context=context)
            if project.is_scrum:
                if 'task_hour_ids' in values: 
                    task_hour_ids = values['task_hour_ids']
                    sum = 0.0
                    for hour in task_hour_ids:
                        sum += hour[2]['expected_hours']
                    values['planned_hours'] = sum
        return super(Task, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context)[0]:
            if task.project_id.is_scrum:
                if 'task_hour_ids' in values:
                    sum = 0.0
                    for hour in values['task_hour_ids']:
                        if hour[0] == 0:
                            sum += hour[2]['expected_hours']
                        elif hour[0] == 1:
                            if 'expected_hours' in hour[2]:
                                sum += hour[2]['expected_hours']
                            else:
                                task_hour_obj = self.pool.get('project.task.hour')
                                task_hour = task_hour_obj.browse(cr, uid , hour[1], context=context)
                                sum += task_hour.expected_hours
                        elif hour[0] == 4:
                            task_hour_obj = self.pool.get('project.task.hour')
                            task_hour = task_hour_obj.browse(cr, uid , hour[1], context=context)
                            sum += task_hour.expected_hours
                    values['planned_hours'] = sum
            super(Task, self).write(cr, uid, task.id, values, context)
        return True

    _defaults = {
        'state': 'draft',
        }
