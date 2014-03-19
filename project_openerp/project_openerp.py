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
    
    _name = 'project.oerp.work.type'
    
    _order = 'sequence'
    
    _columns = {
                'name': fields.char('Type Name', size=128, required=True),
                'sequence': fields.integer('Sequence', required=True),
                'column_number': fields.integer('Column Number', required=True),
                'phase_id': fields.many2one('project.phase', string='Phase', required=True),
                }
    
    _defaults = {
                 'phase_id': lambda slf, cr, uid, ctx: ctx.get('phase_id', False),
                 }
    
class Sprint(osv.Model):
    
    _inherit = 'project.scrum.sprint'
    
    _columns = {
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
                'product_backlog_id': fields.many2one('project.scrum.product.backlog', string='Product Backlog',
                    domain="[('project_id','=',project_id)]"),
                'work_type_ids': fields.one2many('project.oerp.work.type', 'phase_id', string='Work Types'),
                'sprint_ids': fields.one2many('project.scrum.sprint', 'phase_id',
                    string='Sprints'),
                }
    
    _constraints = [(_check_sprints, 'All sprints must belong to the selected '
                     'product backlog.',['Sprints'])]
    
class FeatureHours(osv.Model):
    
    _name = 'project.oerp.feature.hours'
    
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
                'feature_id': fields.many2one('project.scrum.feature', string='Feature', required=True,
                    ondelete='cascade'),
                'project_id': fields.related('feature_id', 'product_backlog_id', 'project_id',
                    type='many2one', relation='project.project', string='Project'),
                'phase_id': fields.many2one('project.phase', string="Phase", 
                    domain="[('project_id','=',project_id)]"),
                'work_type_id': fields.many2one('project.oerp.work.type', string='Work Type',
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
    
    _inherit = 'project.scrum.feature'
    
    def onchange_product_backlog(self, cr, uid, ids, product_backlog_id, context=None):
        res = {}
        if product_backlog_id:
            product_backlog = self.pool.get('project.scrum.product.backlog').browse(
                cr, uid, product_backlog_id, context=context)
            res = {'value': {'project_id': product_backlog.project_id.id}}
        return res
    
    _columns = {
                'hour_ids': fields.one2many('project.oerp.feature.hours', 'feature_id', string='Feature Hours'),
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
                    hour_obj = self.pool.get('project.oerp.feature.hours')
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
                    hour_obj = self.pool.get('project.oerp.feature.hours')
                    sum += hour_obj.browse(cr, uid, id, context=context).expected_hours
            values['expected_hours'] = sum
        return super(Feature,self).create(cr, uid, values, context=context)
    
class Task(osv.Model):
    
    _inherit = 'project.task'
    
    def onchange_sprint(self, cr, uid, ids, sprint_id, context=None):
        res = super(Task,self).onchange_sprint(cr, uid, ids, sprint_id, context=context)
        if sprint_id:
            sprint = self.pool.get('project.scrum.sprint').browse(
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
    
    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids,list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context):
            if task.sprint_id and task.sprint_id.phase_id:
                values['phase_id'] = task.sprint_id.phase_id.id
            super(Task,self).write(cr, uid, task.id, values, context=context)
        return True
    
    _columns = {
                'hour_ids': fields.related('feature_id', 'hour_ids', type='one2many',
                    relation='project.oerp.feature.hours', string='hour_ids', readonly=True)
                }
    
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
                'work_type_id': fields.many2one('project.oerp.work.type', string='Work Type',
                    domain="[('phase_id','=',phase_id)]"),
                }
    
    _defaults = {
                 'phase_id': lambda slf, cr, uid, ctx: ctx.get('phase_id',False),
                 }
    
    _constraints = [(_check_work_type,'The selected Work Type has not been '
                     'planned in the selected Feature.',['Work Type'])]