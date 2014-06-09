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

class WorkType(osv.Model):
    
    _name = 'ccorp.project.oerp.work.type'
    
    _order = 'sequence'
    
    _columns = {
                'name': fields.char('Type Name', size=128, required=True),
                'sequence': fields.integer('Sequence', required=True),
                'column_number': fields.integer('Column Number', required=True),
                'phase_id': fields.many2one('project.phase', ondelete='cascade',
                    string='Phase', required=True),
                }
    
    _defaults = {
                 'phase_id': lambda slf, cr, uid, ctx: ctx.get('phase_id', False),
                 }
    
    
class WorkTypeMapping(osv.Model):
    
    _name = 'ccorp.project.oerp.work.type.mapping'
    
    _columns = {
                'template_id': fields.many2one('ccorp.project.oerp.work.type.template', string='Template',
                    ondelete='cascade'),
                'name': fields.char('Type Name', size=128, translate=True, required=True),
                'sequence': fields.integer('Sequence', required=True),
                'column_number': fields.integer('Column Number', required=True),
                }
    
class WorkTypeTemplate(osv.Model):
    
    _name = 'ccorp.project.oerp.work.type.template'
    
    _columns = {
                'name': fields.char('Template', size=128, translate=True, required=True),
                'group_id': fields.many2one('ccorp.project.oerp.work.type.template.group', string='Group'),
                'file': fields.related('group_id', 'file', type='binary', string='File'),
                'filename': fields.related('group_id','filename', type='char', string='Filename'),
                'work_type_mapping_ids': fields.one2many('ccorp.project.oerp.work.type.mapping', 'template_id',
                    string='Work Types')
                }
    
class WorkTypeTemplateGroup(osv.Model):
    
    _name = 'ccorp.project.oerp.work.type.template.group'
    
    _columns = {
                'name': fields.char('Group Name', size=128, translate=True, required=True),
                'file': fields.binary('File', filters='*.csv'),
                'filename': fields.char('Filename', size=128),
                'template_ids': fields.one2many('ccorp.project.oerp.work.type.template', 'group_id',
                    string='Templates'),
                }
    
    _defaults = {
                 'filename': 'template.csv'
                 }
    
class Sprint(osv.Model):
    
    def tasks_from_features(self, cr, uid, ids, context=None):
        super(Sprint, self).tasks_from_features(cr, uid, ids, context=context)
        sprint = self.browse(cr, uid, ids[0], context=context)
        task_obj = self.pool.get('project.task')
        task_ids = []
        for task in sprint.task_ids:
            task.write({'sprint_id': False}, context=context)
            task_ids.append(task.id)
        for id in task_ids:
            self.write(cr, uid, ids[0],{'desirable_task_ids': [[4,id]]}, context=context)
        return True
    
    def queue_tasks(self, cr, uid, ids, context=None):
        sprint = self.browse(cr, uid, ids[0], context=context)
        for task in sprint.desirable_task_ids:
                if not task.sprint_id:
                    task.write({'sprint_id': sprint.id}, context=context)
        return True
    
    _inherit = 'ccorp.project.scrum.sprint'
    
    _columns = {
                'desirable_task_ids': fields.many2many('project.task', string='Desirable Tasks'),
                'phase_id': fields.many2one('project.phase', string='Phase', required=True,
                    domain="[('project_id','=', project_id)]"),
                }
    
class Phase(osv.Model):
    
    _inherit = 'project.phase'
    
    def onchange_project(self, cr, uid, ids, project_id, context=None):
        res = super(Phase, self).onchange_project(cr,uid,ids,project_id,context=context)
        if project_id:
            project = self.pool.get('project.project').browse(
                cr, uid, project_id, context=context)
            is_scrum = project.is_scrum
            if 'value' in res:
                res['value']['is_scrum'] = is_scrum
                res['value']['product_backlog_id'] = False
            else:
                res['value'] = {
                                'is_scrum': is_scrum,
                                'product_backlog_id': False,
                                }
                
        else:
            if 'value' in res:
                res['value']['is_scrum'] = False
                res['value']['product_backlog_id'] = False
            else:
                res['value'] = {
                                'is_scrum': False,
                                'product_backlog_id': False,
                                }
        return res
    
    def _check_sprints(self, cr, uid, ids, context=None):
        phases = self.browse(cr, uid, ids, context=context)
        for phase in phases:
            for sprint in phase.sprint_ids:
                if sprint.product_backlog_id != phase.product_backlog_id:
                    return False
        return True
    
    _columns = {
                'is_scrum': fields.related('project_id','is_scrum', type='boolean', string='Is Scrum', readonly=True),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog', string='Product Backlog',
                    domain="[('project_id','=',project_id)]"),
                'work_type_ids': fields.one2many('ccorp.project.oerp.work.type', 'phase_id', string='Work Types'),
                'sprint_ids': fields.one2many('ccorp.project.scrum.sprint', 'phase_id',
                    string='Sprints'),
                'user_id': fields.many2one('res.users', string='Phase Manager'),
                }
    
    _constraints = [(_check_sprints, 'All sprints must belong to the selected '
                     'product backlog.',['Sprints'])]
    
class FeatureHours(osv.Model):
    
    _name = 'ccorp.project.oerp.feature.hours'
    
    def _effective_hours(self, cr ,uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid, [('feature_id','=', hour.feature_id.id)], context=context)
            tasks = task_obj.browse(cr, uid, task_ids, context=context)
            sum = 0.0
            for task in tasks:
                for work in task.work_ids:
                    if work.work_type_id == hour.work_type_id:
                        sum += work.hours
            res[hour.id] = sum
        return res
    
    def _remaining_hours(self, cr ,uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            res[hour.id] = hour.expected_hours - hour.effective_hours
        return res
    
    _columns = {
                'feature_id': fields.many2one('ccorp.project.scrum.feature', string='Feature', required=True,
                    ondelete='cascade'),
                'project_id': fields.related('feature_id', 'product_backlog_id', 'project_id',
                    type='many2one', relation='project.project', string='Project'),
                'phase_id': fields.many2one('project.phase', string="Phase", 
                    domain="[('project_id','=',project_id)]"),
                'work_type_id': fields.many2one('ccorp.project.oerp.work.type', string='Work Type',
                    required=True, domain="[('phase_id','=',phase_id)]"),
                'expected_hours': fields.float('Planned Hour(s)', required=True),
                'effective_hours': fields.function(_effective_hours, type='float', string='Spent Hour(s)'),
                'remaining_hours': fields.function(_remaining_hours, type='float', string='Remaining Hour(s)'),
                }
    
    _defaults = {
                 'feature_id': lambda slf, cr, uid, ctx: ctx.get('feature_id', False),
                 'project_id': lambda slf, cr, uid, ctx: ctx.get('project_id', False),
                 }
    
class Feature(osv.Model):
    
    _inherit = 'ccorp.project.scrum.feature'
    
    def onchange_product_backlog(self, cr, uid, ids, product_backlog_id, context=None):
        res = {}
        if product_backlog_id:
            product_backlog = self.pool.get('ccorp.project.scrum.product.backlog').browse(
                cr, uid, product_backlog_id, context=context)
            res = {'value': {'project_id': product_backlog.project_id.id}}
        return res
    
    _columns = {
                'hour_ids': fields.one2many('ccorp.project.oerp.feature.hours', 'feature_id', string='Feature Hours'),
                }
    
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
                    hour_obj = self.pool.get('ccorp.project.oerp.feature.hours')
                    sum += hour_obj.browse(cr, uid, id, context=context).expected_hours
            values['expected_hours'] = sum
        return super(Feature,self).write(cr, uid, ids, values, context=context)
    
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
                    hour_obj = self.pool.get('ccorp.project.oerp.feature.hours')
                    sum += hour_obj.browse(cr, uid, id, context=context).expected_hours
            values['expected_hours'] = sum
        return super(Feature,self).create(cr, uid, values, context=context)
    
class TaskHours(osv.Model):
    
    _name = 'ccorp.project.oerp.task.hour'
    
    def _effective_hours(self, cr ,uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            work_obj = self.pool.get('project.task.work')
            work_ids = work_obj.search(cr, uid, [('task_id','=', hour.task_id.id),
                ('work_type_id','=',hour.work_type_id.id)], context=context)
            works = work_obj.browse(cr, uid, work_ids, context=context)
            sum = 0.0
            for work in works:
                sum += work.hours
            res[hour.id] = sum
        return res
    
    def _remaining_hours(self, cr ,uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            res[hour.id] = hour.expected_hours - hour.effective_hours
        return res
    
    _columns = {
                'task_id': fields.many2one('project.task', string='Task', required=True, ondelete='cascade'),
                'project_id': fields.related('task_id', 'project_id', type='many2one',
                    relation='project.project', string='Project'),
                'phase_id': fields.many2one('project.phase', string="Phase", 
                    domain="[('project_id','=',project_id)]"),
                'work_type_id': fields.many2one('ccorp.project.oerp.work.type', string='Work Type', required =True,
                    domain="[('phase_id','=',phase_id)]"),
                'expected_hours': fields.float('Initially Planned Hour(s)', required=True),
                'effective_hours': fields.function(_effective_hours, type='float', string='Spent Hour(s)'),
                'remaining_hours': fields.function(_remaining_hours, type='float', string='Remaining Hour(s)'),
                }
    
    _defaults = {
                 'project_id': lambda slf, cr, uid, ctx: ctx.get('project_id', False),
                 'task_id': lambda slf, cr, uid, ctx: ctx.get('task_id', False),
                 }
    
class Task(osv.Model):
    
    _inherit = 'project.task'
    
    def onchange_sprint(self, cr, uid, ids, sprint_id, context=None):
        res = super(Task,self).onchange_sprint(cr, uid, ids, sprint_id, context=context)
        if sprint_id:
            sprint = self.pool.get('ccorp.project.scrum.sprint').browse(
                cr, uid, sprint_id, context=context)
            if 'value' in res:
                res['value']['phase_id'] = sprint.phase_id.id
            else:
                res['value'] = {'phase_id': sprint.phase_id.id}
        else:
            if 'value' in res:
                res['value']['phase_id'] = False
            else:
                res['value'] = {'phase_id': False}
        return res
    
    _columns = {
                'feature_hour_ids': fields.related('feature_id', 'hour_ids', type='one2many',
                    relation='ccorp.project.oerp.feature.hours', string='Feature Hours', readonly=True),
                'task_hour_ids': fields.one2many('ccorp.project.oerp.task.hour', 'task_id', string='Task Hours'),
                }
    
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
        if not isinstance(ids,list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context):
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
                                task_hour_obj = self.pool.get('ccorp.project.oerp.task.hour')
                                task_hour = task_hour_obj.browse(cr, uid , hour[1], context=context)
                                sum += task_hour.expected_hours
                        elif hour[0] == 4:
                            task_hour_obj = self.pool.get('ccorp.project.oerp.task.hour')
                            task_hour = task_hour_obj.browse(cr, uid , hour[1], context=context)
                            sum += task_hour.expected_hours
                    values['planned_hours'] = sum
            super(Task, self).write(cr, uid, task.id, values, context)
        return True
    
class TaskWork(osv.Model):
    
    _inherit = 'project.task.work'
    
    def _check_work_type(self, cr , uid, ids, context=None):
        works = self.browse(cr, uid, ids, context=context)
        for work in works:
            if work.work_type_id:
                if work.task_id.feature_id:
                    feature = work.task_id.feature_id
                    flag = True
                    for hour in feature.hour_ids:
                        if hour.work_type_id == work.work_type_id:
                            flag = False
                    if flag:
                        return False
        return True
    
    _columns = {
                'phase_id': fields.many2one('project.phase', string='Phase'),
                'work_type_id': fields.many2one('ccorp.project.oerp.work.type', string='Work Type',
                    domain="[('phase_id','=',phase_id)]"),
                }
    
    _defaults = {
                 'phase_id': lambda slf, cr, uid, ctx: ctx.get('phase_id',False),
                 }
    
    _constraints = [(_check_work_type,'The selected Work Type has not been '
                     'planned in the selected Feature.',['Work Type'])]