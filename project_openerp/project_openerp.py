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
                'phase_id': fields.many2one('project.phase', string='Phase', required=True),
                }
    
    _defaults = {
                 'phase_id': lambda slf, cr, uid, ctx: ctx.get('phase_id', False),
                 }
    
class Phase(osv.Model):
    
    _inherit = 'project.phase'
    
    _columns = {
                'work_type_ids': fields.one2many('project.oerp.work.type', 'phase_id', string='Work Types'),
                }
    
class FeatureHours(osv.Model):
    
    _name = 'project.oerp.feature.hours'
    
    #TODO: calculate hours from tasks with this work type
    def _effective_hours(self, cr ,uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            task_obj = self.pool.get('project.task')
            #task_ids = task_obj.search(cr, uid, ids, [('feature_id','=', hour.feature_id)], context=context)
            
            res[hour.id] = 0.0
        return res
    
    def _remaining_hours(self, cr ,uid, ids, field_name, arg, context=None):
        res = {}
        for hour in self.browse(cr, uid, ids, context=context):
            res[hour.id] = hour.expected_hours - hour.effective_hours
        return res
    
    _columns = {
                'feature_id': fields.many2one('project.scrum.feature', string='Feature', required=True),
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
    
class TaskWork(osv.Model):
    
    _inherit = 'project.task.work'
    
    _columns = {
                'phase_id': fields.many2one('project.phase', string='Phase'),
                'work_type_id': fields.many2one('project.oerp.work.type', string='Work Type',
                    domain="[('phase_id','=',phase_id)]"),
                }
    
    _defaults = {
                 'phase_id': lambda slf, cr, uid, ctx: ctx.get('phase_id',False),
                 }
