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
from openerp.tools.translate import _
from datetime import datetime

# Mapping between task priority and
# feature priority
PRIORITY = {
            5: '4',
            4: '3',
            3: '2',
            2: '1',
            1: '0',
            }

STATES = [('draft', 'New'),('open', 'In Progress'),
          ('pending', 'Pending'), ('done', 'Done'),
          ('cancelled', 'Cancelled')]

class project(osv.Model):
    
    _inherit = 'project.project'
    
    _columns = {
                'is_scrum': fields.boolean('Scrum'),
                }
    
class featureType(osv.Model):
    
    _name = 'ccorp.project.scrum.feature.type'
    
    _columns = {
                'code': fields.char('Code', size=16, required=True),
                'name': fields.char('Type Name', size=128, required=True, translate=True),
                }
    
    _sql_constraints = [('unique_code','UNIQUE(code)','Code must be unique for every feature type.')]
    
    def name_get(self, cr, uid, ids, context=None):
        res =[]
        for r in self.read(cr, uid, ids, ['code', 'name'], context=context):
            name = '%s - %s' %(r['code'],r['name'])
            res.append((r['id'], name))
        return res
    
class Feature(osv.Model):
    
    _name = 'ccorp.project.scrum.feature'
    
    def _date_start(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the date_start based on the tasks from sprints 
        related to each feature"""
        res = {}
        for id in ids:
            sprint_ids = [x.id for x in
                          self.browse(cr, uid, id,
                              context=context).sprint_ids]
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid,
                                       [('sprint_id','in',sprint_ids),
                                        ('feature_id','=',id),
                                        '!',('state','in',['cancelled','draft'])],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            date_start = False
            for task in tasks:
                if task.date_start:
                    date = datetime.strptime(task.date_start,'%Y-%m-%d %H:%M:%S')
                    if not date_start:
                        date_start = date
                    else:
                        if date_start > date:
                            date_start = date
            if date_start:
                date_start = datetime.strftime(date_start,'%Y-%m-%d %H:%M:%S') 
            res[id] = date_start
        return res
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the end date based on the tasks from sprints 
        related to each feature"""
        res = {}
        for id in ids:
            sprint_ids = [x.id for x in
                          self.browse(cr, uid, id,
                              context=context).sprint_ids]
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid,
                                       [('sprint_id','in',sprint_ids),
                                        ('feature_id','=',id),
                                        '!',('state','in',['cancelled','draft'])],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            date_end = False
            for task in tasks:
                if task.date_end:
                    date = datetime.strptime(task.date_end,'%Y-%m-%d %H:%M:%S')
                    if not date_end:
                        date_end = date
                    else:
                        if date > date_end:
                            date_end = date
            if date_end:
                date_end = datetime.strftime(date_end,'%Y-%m-%d %H:%M:%S') 
            res[id] = date_end
        return res
    
    def _deadline(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the deadline based on the tasks from sprints 
        related to each feature"""
        res = {}
        for id in ids:
            sprint_ids = [x.id for x in
                          self.browse(cr, uid, id,
                              context=context).sprint_ids]
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid,
                                       [('sprint_id','in',sprint_ids),
                                        ('feature_id','=',id),
                                        '!',('state','in',['cancelled','draft'])],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            deadline = False
            for task in tasks:
                if task.date_deadline:
                    date = datetime.strptime(task.date_deadline,'%Y-%m-%d')
                    if not deadline:
                        deadline = date
                    else:
                        if date > deadline:
                            deadline = date
            if deadline:
                deadline = datetime.strftime(deadline,'%Y-%m-%d') 
            res[id] = deadline
        return res
    
    def _effective_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the planned hours based on the tasks from sprints 
        related to each feature"""
        res = {}
        for id in ids:
            sprint_ids = [x.id for x in
                          self.browse(cr, uid, id,
                              context=context).sprint_ids]
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid,
                                       [('sprint_id','in',sprint_ids),
                                        ('feature_id','=',id)],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            sum = reduce(lambda result,task: result+task.effective_hours,
                         tasks, 0.0)
            res[id] = sum
        return res
    
    def _remaining_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the difference between planned and effective hours"""
        res={}
        features = self.browse(cr, uid, ids, context=context)
        for feature in features:
            res[feature.id] = feature.expected_hours - \
            feature.effective_hours
        return res
    
    def _progress(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the total progress based on the tasks from sprints 
        related to each feature"""
        res = {}
        for id in ids:
            sprint_ids = [x.id for x in
                          self.browse(cr, uid, id,
                              context=context).sprint_ids]
            task_obj = self.pool.get('project.task')
            task_ids = task_obj.search(cr, uid,
                                       [('sprint_id','in',sprint_ids),
                                        ('feature_id','=',id)],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            if tasks:
                sum = reduce(lambda result,task: result+task.progress,
                             tasks, 0.0)
                res[id] = sum/len(tasks)
            else:
                res[id] = 0.0
        return res
    
    def set_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)
    
    def set_approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)
    
    def set_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
    
    def set_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)
    
    def set_very_low_priority(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'priority':5}, context=context)
    
    def set_low_priority(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'priority':4}, context=context)
    
    def set_medium_priority(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'priority':3}, context=context)
    
    def set_high_priority(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'priority':2}, context=context)
    
    def set_very_high_priority(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'priority':1}, context=context)
    
    def _check_release_backlog(self, cr, uid, ids, context=None):
        for feature in self.browse(cr, uid, ids, context=context):
            if feature.release_backlog_id and \
            not feature.release_backlog_id in \
            feature.product_backlog_id.release_backlog_ids:
                return False
        return True
    
    _columns = {
                'name': fields.char('Feature Name', size=128, required=True),
                'code': fields.char('Code', size=16, required=True),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog',
                    string='Product Backlog', required=True, domain="[('state','in',['draft','open','pending'])]"),
                'release_backlog_id': fields.many2one('ccorp.project.scrum.release.backlog',
                    string='Release Backlog', domain="[('product_backlog_id','=',product_backlog_id),"
                    "'|',('state','=','open'),('state','=','pending')]"),
                'project_id': fields.related('product_backlog_id', 'project_id', type='many2one',
                    relation='project.project', string='Project', store=True),
                'user_id': fields.related('product_backlog_id', 'user_id', type='many2one',
                    relation='res.users', string='Scrum Master', store=True),
                'description': fields.text('Description'),
                'partner_id': fields.many2one('res.partner', string='Product Owner',
                    domain="[('customer','=',True)]",
                    help='Contact or person responsible of keeping the '
                    'business perspective in scrum projects.'),
                'type_id': fields.many2one('ccorp.project.scrum.feature.type', string='Type'),
                'priority': fields.selection([(5, '5 - Very Low'),(4,'4 - Low'),(3,'3 - Medium'),(2,'2 - High'),
                    (1,'1 - Very High')], string='Priority', required=True),
                'sprint_ids': fields.many2many(
                    'ccorp.project.scrum.sprint', readonly=True, string='Sprints',
                    rel='project_scrum_sprint_backlog',
                    help='Sprints in which the feature has been used.'),
                'task_ids': fields.one2many('project.task', 'feature_id', string='Tasks', readonly=True),
                'date_start': fields.function(_date_start, type='datetime', string='Start Date'),
                'date_end': fields.function(_date_end, type='datetime', string='End Date'),
                'deadline': fields.function(_deadline, type='date', string='Deadline'),
                'expected_hours': fields.float('Initially Planned Hour(s)',
                    help='Total planned hours for the development of '
                    'this feature.\nRecommended values are:\n 1h, 2h, 4h,'
                    ' or 8h'),
                'effective_hours': fields.function(
                    _effective_hours, type='float', string='Spent Hour(s)',
                    help='Total effective hours from tasks related to this feature.'),
                'remaining_hours': fields.function(
                    _remaining_hours, type='float', string='Remaining Hour(s)',
                    help='Difference between planned hours and spent hours.'),
                'progress': fields.function(_progress, type='float', string='Progress (%)'),
                'state': fields.selection([('draft','New'), ('approved','Approved'),
                    ('open','In Progress'), ('cancelled', 'Cancelled'),('done','Done'),],
                    'Status', required=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'priority': 3,
                 'state': 'draft',
                 'product_backlog_id': lambda self, cr, uid, c: c.get('product_backlog_id', False),
                 'release_backlog_id': lambda self, cr, uid, c: c.get('release_backlog_id', False),
                 }
    
    def name_get(self, cr, uid, ids, context=None):
        res =[]
        for r in self.read(cr, uid, ids, ['code', 'name'], context=context):
            name = '%s - %s' %(r['code'],r['name'])
            res.append((r['id'], name))
        return res
    
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=50):
        ids = []
        if name:
            ids = self.search(cr, uid,
                              ['|',('code',operator,name),
                               ('name',operator,name)] + args,
                              limit=limit, context=context)
        else:
            ids  = self.search(cr, uid, args, limit=limit, context=context)
        
        return self.name_get(cr, uid, ids, context=context)
    
    def copy(self, cr, uid, id, defaults, context=None):
        feature = self.browse(cr, uid, id, context=context)
        defaults['code'] = feature.code + ' (copy)'
        return super(Feature, self).copy(cr, uid, id, defaults, context=context)
    
    _constraints = [(_check_release_backlog,'The selected Release Backlog must belong to '
                     'the selected Product Backlog',['Release Backlog'])]
    
    _sql_constraints = [('unique_code_product','UNIQUE(code,product_backlog_id)',
                         'Code must be unique for every feature related to a Product Backlog')]
    
class Sprint(osv.Model):
    
    _name = 'ccorp.project.scrum.sprint'
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate End date as the highest End Date from
        tasks related to this sprint"""
        res = {}
        for id in ids:
            tasks = self.browse(cr, uid, id, context=context).task_ids
            date_end = False
            for task in tasks:
                if task.date_end and task.state not in ('draft','cancelled'):
                    date = datetime.strptime(task.date_end, '%Y-%m-%d %H:%M:%S')
                    if not date_end:
                        date_end = date
                    else:
                        if date > date_end:
                            date_end = date
            if date_end:
                date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')
            res[id] = date_end
        return res
    
    def _expected_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the expected hours from features  related to this
        sprint."""
        res = {}
        for id in ids:
            features = self.browse(cr, uid, id, context=context).feature_ids
            sum = reduce(lambda result,feature: result+feature.expected_hours,
                         features, 0.0)
            res[id] = sum
        return res
    
    def _effective_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the effective hours using the work done in tasks
        related to this sprint."""
        res = {}
        for id in ids:
            tasks = self.browse(cr, uid, id, context=context).task_ids
            sum = reduce(lambda result,task: result+task.effective_hours,
                         tasks, 0.0)
            res[id] = sum
        return res
    
    def _remaining_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the difference between planned and effective hours."""
        res = {}
        sprints = self.browse(cr, uid, ids, context=context)
        for sprint in sprints:
            res[sprint.id] = sprint.expected_hours - sprint.effective_hours
        return res
    
    def _progress(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the progress using the progress in tasks related
        to this sprint."""
        res = {}
        for id in ids:
            tasks = self.browse(cr, uid, id, context=context).task_ids
            if tasks:
                sum = reduce(lambda result,task: result+task.progress,
                             tasks, 0.0)
                res[id] = sum/len(tasks)
            else:
                # set a zero if no tasks are available
                res[id] = 0.0
        return res
    
    def onchange_product_backlog(self, cr, uid, ids, product_backlog_id, context=None):
        vals = {}
        if product_backlog_id:
            backlog = self.pool.get('ccorp.project.scrum.product.backlog').browse(
                cr,uid,product_backlog_id,context=context)
            vals['project_id'] = backlog.project_id.id
        else:
            vals['project_id'] = False
        return {'value': vals}
    
    def onchange_project(self, cr, uid, ids, project_id, stage_id, context=None):
        if project_id:
            type_ids = [x.id for x in self.pool.get('project.project').browse(
                cr, uid, project_id, context=context).type_ids]
            if not stage_id in type_ids: 
                stage = self.get_default_stage_id(cr, uid, project_id, context=context)
                return {'value': {'stage_id': stage}}
            else: 
                return {}
        return {
                'value': {
                          'stage_id': self.get_default_stage(cr, uid, context=context)
                          }
                }
    
    def get_default_stage(self, cr ,uid, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr, uid, [('state','=','draft')],
            context=context, limit=1)[0]
        if not type:
            raise osv.except_osv(_('Error'),_('There is no ''draft'' state configured.'))
        return type
        
    def get_default_stage_id(self, cr ,uid, project_id, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,
            [('project_ids','=',project_id)], context=context, limit=1)[0]
        return type
    
    def tasks_from_features(self, cr, uid, ids, context=None):
        sprint = self.browse(cr, uid, ids[0], context=context)
        task_obj = self.pool.get('project.task')
        for feature in sprint.feature_ids:
            values = {
                      'project_id': sprint.project_id.id,
                      'product_backlog_id': sprint.product_backlog_id.id,
                      'release_backlog_id': sprint.release_backlog_id.id,
                      'sprint_id': sprint.id,
                      'feature_id': feature.id,
                      'user_id': uid,
                      'planned_hours': feature.expected_hours,
                      'remaining_hours': feature.expected_hours,
                      'date_start': sprint.date_start,
                      'date_end': sprint.deadline,
                      'date_deadline': sprint.deadline,
                      'priority': PRIORITY[feature.priority],
                      'description': feature.description,
                      'name': feature.code + ' ' + feature.name,
                      }
            task_obj.create(cr, uid, values, context=context)
        return True
    
    def set_features_done(self, cr, uid, ids, context=None):
        sprint = self.browse(cr, uid, ids[0], context=context)
        for feature in sprint.feature_ids:
            if not feature.state in ('done','cancelled'):
                feature.write({'state': 'done'}, context=context)
        return True
    
    def set_done(self, cr, uid, ids, context=None):
        if not isinstance(ids,list):
            ids = [ids]
        sprint = self.browse(cr, uid, ids[0], context=context)
        for task in sprint.task_ids:
            if not task.state in ['done','cancelled']:
                raise osv.except_osv(_('Error'),
                    _('All tasks must be done or cancelled in order '
                      'to cancel this sprint.'))
        project = sprint.project_id
        id = False
        for stage in project.type_ids:
            if stage.state == 'done':
                id = stage.id
                break
        self.write(cr, uid, ids[0], {'stage_id': id}, context)
        return True
    
    def set_cancel(self, cr, uid, ids, context=None):
        sprint = self.browse(cr, uid, ids[0], context=context)
        for task in sprint.task_ids:
            if not task.state in ['done','cancelled']:
                raise osv.except_osv(_('Error'),
                    _('All tasks must be done or cancelled in order '
                      'to cancel this sprint.'))
        project = sprint.project_id
        id = False
        for stage in project.type_ids:
            if stage.state == 'cancelled':
                id = stage.id
                break
        self.write(cr, uid, ids[0], {'stage_id': id}, context)
        return True
    
    def _check_release_backlog(self, cr, uid, ids, context=None):
        sprints = self.browse(cr, uid, ids, context=context)
        for sprint in sprints:
            if sprint.release_backlog_id and sprint.product_backlog_id:
                if sprint.release_backlog_id.product_backlog_id != sprint.product_backlog_id:
                    return False
        return True
    
    def _check_deadline(self, cr, uid, ids, context=None):
        sprints = self.browse(cr, uid, ids, context=context)
        for sprint in sprints:
            date_start = datetime.strptime(sprint.date_start, '%Y-%m-%d %H:%M:%S')
            deadline = datetime.strptime(sprint.deadline, '%Y-%m-%d')
            if deadline < date_start:
                return False
        return True
    
    _columns = {
                'name': fields.char('Sprint Name', size=128, required=True),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog',
                    string='Product Backlog', domain="['|',('state','=','open'),"
                    "('state','=','pending')]", required=True),
                'release_backlog_id': fields.many2one('ccorp.project.scrum.release.backlog',
                    required=True, string='Release Backlog', domain="[('product_backlog_id','=',product_backlog_id),"
                    "'|',('state','=','open'),('state','=','pending')]"),
                'project_id': fields.related('release_backlog_id','product_backlog_id','project_id',
                    relation='project.project', type='many2one', string='Project', store=True, readonly=True),
                'user_id': fields.related('release_backlog_id','product_backlog_id','project_id', 'user_id',
                    relation='res.users', type='many2one', string='Scrum Master', store=True),
                'member_ids': fields.related('release_backlog_id','product_backlog_id','project_id', 'members',
                    relation='res.users', type='many2many', string='Team Members', readonly=True),
                'task_ids': fields.one2many('project.task', 'sprint_id', string='Tasks'),
                'feature_ids': fields.many2many('ccorp.project.scrum.feature', rel='project_scrum_sprint_backlog',
                    string='Features', help='Features to be developed in this sprint', 
                    domain="[('state','in',['approved','open']),('release_backlog_id','=',release_backlog_id),"
                    "('release_backlog_id','!=',False)]"),
                'date_start': fields.datetime('Start Date', required=True),
                'date_end': fields.function(_date_end, type='datetime', string='End Date'),
                'deadline': fields.date('Deadline', required=True),
                'expected_hours': fields.function(_expected_hours, type='float', string='Initially Planned Hour(s)'),
                'effective_hours': fields.function(_effective_hours, type='float', string='Spent Hour(s)'),
                'remaining_hours': fields.function(_remaining_hours, type='float', string='Remaining Hour(s)'),
                'progress': fields.function(_progress, type='float', string='Progress (%)'),
                'stage_id': fields.many2one('project.task.type', string='Stage', domain="['&', ('fold', '=', False),"
                    " ('project_ids', '=', project_id)]"),
                'state': fields.related('stage_id', 'state', type='selection', string='State', readonly=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'date_start': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
                 'deadline': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d'),
                 'stage_id': get_default_stage,
                 'product_backlog_id': lambda self, cr, uid, c: c.get('product_backlog_id', False),
                 'release_backlog_id': lambda self, cr, uid, c: c.get('release_backlog_id', False),
                 }
    
    _constraints = [(_check_release_backlog,'The selected Release Backlog must belong to '
                     'the selected Product Backlog',['Release Backlog']),
                    (_check_deadline, 'Deadline must be greater than Start Date',['Start Date','Deadline'])]
    
class Task(osv.Model):
    
    _inherit = 'project.task'
    
    def _end_date(self, works):
        date_end = False
        for work in works:
            if work.date:
                date = datetime.strptime(work.date,'%Y-%m-%d %H:%M:%S')
                if not date_end:
                    date_end = date
                else:
                    if date_end < date:
                        date_end = date
        if date_end:
            return datetime.strftime(date_end,'%Y-%m-%d %H:%M:%S')
        return date_end
    
    def onchange_project(self, cr, uid, ids, project_id, context=None):
        res = super(Task,self).onchange_project(cr,uid,ids,project_id,context=context)
        if project_id:
            project = self.pool.get('project.project').browse(
                cr, uid, project_id, context=context)
            if not 'value' in res:
                res['value'] = {}
            res['value']['is_scrum'] = project.is_scrum
            if not project.is_scrum:
                res['value']['product_backlog_id'] = False
                res['value']['release_backlog_id'] = False
                res['value']['sprint_id'] = False
                res['value']['feature_id'] = False
        else:
            if not 'value' in res:
                res['value'] = {}
            res['value']['is_scrum'] = False
            res['value']['product_backlog_id'] = False
            res['value']['release_backlog_id'] = False
            res['value']['sprint_id'] = False
            res['value']['feature_id'] = False
        return res
    
    def onchange_sprint(self, cr, uid, ids, sprint_id, context=None):
        res = None
        if sprint_id:
            res = {
                   'value': {},
                   'domain': {},
                   }
            sprint_obj = self.pool.get('ccorp.project.scrum.sprint')
            sprint = sprint_obj.browse(cr,uid,sprint_id,context=context)
            res['value']['date_deadline'] = sprint.deadline
            member_ids = [x.id for x in sprint.member_ids]
            res['domain']['user_id'] = [('id','in',member_ids)]
        else:
            res = {'value': {}}
            res['value']['date_deadline'] = False
        return res
    
    def onchange_feature(self, cr, uid, ids, feature_id, context=None):
        if feature_id:
            feature = self.pool.get('ccorp.project.scrum.feature').browse(
                cr,uid,feature_id,context=context)
            return {
                    'value': {
                              'planned_hours': feature.expected_hours,
                              'priority': PRIORITY[feature.priority],
                              }
                    }
        else:
            return {
                'value': {
                          'planned_hours': False,
                          'priority': '2',
                          }
                }
    def _check_product_backlog(self, cr, uid, ids, context=None):
        tasks = self.browse(cr, uid, ids, context=context)
        for task in tasks:
            if task.product_backlog_id and \
            task.product_backlog_id.project_id != task.project_id:
                return False
        return True
    
    def _check_release_backlog(self, cr, uid, ids, context=None):
        tasks = self.browse(cr, uid, ids, context=context)
        for task in tasks:
            if task.release_backlog_id and \
            task.release_backlog_id.product_backlog_id != task.product_backlog_id:
                return False
        return True
    
    def _check_sprint(self, cr, uid, ids, context=None):
        tasks = self.browse(cr, uid, ids, context=context)
        for task in tasks:
            if task.sprint_id and \
            task.sprint_id.release_backlog_id != task.release_backlog_id:
                return False
        return True
    
    def _check_feature(self, cr, uid, ids, context=None):
        tasks = self.browse(cr, uid, ids, context=context)
        for task in tasks:
            if task.sprint_id and task.feature_id:
                if not task.feature_id in task.sprint_id.feature_ids:
                    return False
        return True
    
    def _check_related_tasks(self, cr ,uid, ids, context=None):
        tasks = self.browse(cr, uid, ids, context=context)
        for task in tasks:
            for previous_task in task.previous_task_ids:
                if previous_task.id == task.id or \
                previous_task in task.next_task_ids:
                    return False
            for next_task in task.next_task_ids:
                if next_task.id == task.id:
                    return False
        return True
    
    _columns = {
                'is_scrum': fields.boolean('Scrum'),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog', string='Product Backlog',
                    domain="[('project_id','=',project_id),'|',('state','=','open'),('state','=','pending')]"),
                'release_backlog_id': fields.many2one('ccorp.project.scrum.release.backlog', string='Release Backlog',
                    domain="[('product_backlog_id','=',product_backlog_id),'|',('state','=','open'),"
                    "('state','=','pending')]"),
                'sprint_id': fields.many2one('ccorp.project.scrum.sprint', string='Sprint',
                    domain ="[('release_backlog_id','=',release_backlog_id),'|',('state','=','open'),"
                    "('state','=','pending')]"),
                'feature_id': fields.many2one('ccorp.project.scrum.feature', string='Feature',
                    domain="[('sprint_ids','=',sprint_id),('state','in',['open','approved'])]"),
                'feature_type_id': fields.related('feature_id','type_id', type='many2one', string='Feature Type',
                    relation='ccorp.project.scrum.feature.type', readonly=True),
                'previous_task_ids': fields.many2many('project.task', 'ccorp_project_scrum_task_previous_tasks',
                    'task_id', 'previous_task_id', string='Previous Tasks', domain="['!',('id','=',id)]"),
                'next_task_ids': fields.many2many('project.task', 'ccorp_project_scrum_task_next_tasks',
                    'task_id', 'next_task_id', string='Next Tasks', domain="['!',('state','in',['done','cancelled']),"
                    "'!',('id','=',id)]"),
                }
    
    _defaults = {
                 'date_start': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
                 'date_end': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
                 'project_id': lambda slf, cr, uid, ctx: ctx.get('project_id', False),
                 'product_backlog_id': lambda slf, cr, uid, ctx: ctx.get('product_backlog_id', False),
                 'release_backlog_id': lambda slf, cr, uid, ctx: ctx.get('release_backlog_id', False),
                 'sprint_id': lambda slf, cr, uid, ctx: ctx.get('sprint_id', False),
                 }
    
    _constraints = [
                    (_check_product_backlog, 'The selected Product Backlog must belong to '
                     'the selected Project.',['Product Backlog']),
                    (_check_release_backlog, 'The selected Release Backlog must belong to '
                     'the selected Product Backlog.',['Release Backlog']),
                    (_check_sprint, 'The selected Sprint must belong to the selected '
                     'Release Backlog.',['Sprint']),
                    (_check_feature, 'The selected Feature must belong to the selected '
                     'Sprint.',['Feature']),
                    (_check_related_tasks, 'There was an error checking the relationship between tasks. '
                     'Please check if you selected an invalid task.', ['Previous Tasks','Next Tasks']),
                    ]
    
class releaseBacklog(osv.Model):
    
    _name = 'ccorp.project.scrum.release.backlog'
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the end date from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            date_end = False
            for sprint in sprints:
                if sprint.date_end and sprint.state not in ['draft','cancelled']:
                    date = datetime.strptime(sprint.date_end, '%Y-%m-%d %H:%M:%S')
                    if not date_end:
                        date_end = date
                    else:
                        if date_end < date:
                            date_end = date
            if date_end:
                date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')
            res[id] = date_end
        return res
    
    def _date_start(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the start date from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            date_start = False
            for sprint in sprints:
                if sprint.date_start and sprint.state not in ['draft','cancelled']:
                    date = datetime.strptime(sprint.date_start, '%Y-%m-%d %H:%M:%S')
                    if not date_start:
                        date_start = date
                    else:
                        if date_start > date:
                            date_start = date
            if date_start:
                date_start = date_start.strftime('%Y-%m-%d %H:%M:%S')
            res[id] = date_start
        return res
    
    def _deadline(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the deadline from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            deadline = False
            for sprint in sprints:
                if not sprint.deadline and sprint.state not in ['draft','cancelled']:
                    date = datetime.strptime(sprint.deadline, '%Y-%m-%d')
                    if not deadline:
                        deadline = date
                    else:
                        if deadline < date:
                            deadline = date
            if deadline:
                deadline = deadline.strftime('%Y-%m-%d')
            res[id] = deadline
        return res
    
    def _expected_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the expected hours from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            sum = reduce(lambda result,sprint: result+sprint.expected_hours,
                         sprints, 0.0)
            res[id] = sum
        return res
    
    def _effective_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the effective hours from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            sum = reduce(lambda result,sprint: result+sprint.effective_hours,
                         sprints, 0.0)
            res[id] = sum
        return res
    
    def _remaining_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the difference between expected and effective hours
        from sprints related to each backlog"""
        res = {}
        releases = self.browse(cr, uid, ids, context=context)
        for release in releases:
            res[release.id] = release.expected_hours - release.effective_hours
        return res
    
    def _progress(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the total progress from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            if sprints:
                sum = reduce(lambda result,sprint: result+sprint.progress,
                             sprints, 0.0)
                res[id] = sum/len(sprints)
            else:
                res[id] = 0.0
        return res
    
    def onchange_product_backlog(self, cr, uid, ids, backlog_id, context=None):
        value = {
                 'project_id': False,
                 }
        if backlog_id:
            project_id = self.pool.get('ccorp.project.scrum.product.backlog').browse(
                cr,uid,backlog_id,context=context).project_id.id
            value['project_id'] = project_id
        return {
                'value': value
                }
    
    def _set_done(self, cr, uid, ids, context=None):
        project = self.browse(cr, uid, ids[0], context=context).project_id
        for stage in project.type_ids:
            if stage.state == 'done':
                return self.write(cr, uid, ids[0], {'stage_id':stage.id}, context=context)
        raise osv.except_osv(_('Error'), _('There is no done state configured for'
                             ' the project %s') %project.name)
    
    def do_done(self, cr, uid, ids, context=None):
        sprints = self.browse(cr,uid,ids[0],context=context).sprint_ids
        for sprint in sprints:
            if sprint.state != 'cancelled' and sprint.state != 'done':
                raise osv.except_osv(_('Error'),_('You can not set as done a release backlog if '
                                     'all sprints related to it are not cancelled'
                                     ' or done'))
        return self._set_done(cr, uid, ids, context=context)
    
    def _set_cancel(self, cr, uid, ids, context=None):
        project = self.browse(cr, uid, ids[0], context=context).project_id
        for stage in project.type_ids:
            if stage.state == 'cancelled':
                return self.write(cr, uid, ids[0], {'stage_id':stage.id}, context=context)
        raise osv.except_osv(_('Error'), _('There is no cancelled state configured for'
                             ' the project %s') %project.name)
    
    def do_cancel(self, cr, uid, ids, context=None):
        sprints = self.browse(cr,uid,ids[0],context=context).sprint_ids
        for sprint in sprints:
            if sprint.state != 'cancelled' and sprint.state != 'done':
                raise osv.except_osv(_('Error'),_('You can not cancel a release backlog if '
                                     'all sprints related to it are not cancelled'
                                     ' or done'))
        return self._set_cancel(cr, uid, ids, context=context)
    
    def onchange_project(self, cr, uid, ids, project_id, stage_id, context=None):
        if project_id:
            type_ids = [x.id for x in self.pool.get('project.project').browse(
                cr, uid, project_id, context=context).type_ids]
            if not stage_id in type_ids: 
                stage = self.get_default_stage_id(cr, uid, project_id, context=context)
                return {
                        'value': {
                                  'stage_id': stage
                                  }
                        }
            else: 
                return {}
        return {
                'value': {
                          'stage_id': self.get_default_stage(cr, uid, context=context)
                          }
                }
    
    def get_default_stage(self, cr ,uid, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,[('state','=','draft')],
            context=context, limit=1)[0]
        if not type:
            raise osv.except_osv(_('Error'),_('There is no ''draft'' state configured.'))
        return type
        
    def get_default_stage_id(self, cr ,uid, project_id, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,
            [('project_ids','=',project_id)], context=context, limit=1)[0]
        return type
    
    _columns = {
                'name': fields.char('Release Name', size=128, required=True),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog',
                    string= 'Product Backlog', required=True, domain="[('state','in',['open','pending'])]"),
                'project_id': fields.related('product_backlog_id', 'project_id', type='many2one',
                    relation='project.project', string='Project', readonly=True, store=True),
                'user_id': fields.related('product_backlog_id', 'project_id','user_id', type='many2one',
                    relation='res.users', string='Project', readonly=True, store=True),
                'feature_ids': fields.one2many('ccorp.project.scrum.feature','release_backlog_id',
                    string='Features'),
                'sprint_ids': fields.one2many('ccorp.project.scrum.sprint', 'release_backlog_id',
                    string='Sprints'),
                'date_start': fields.function(_date_start, type='datetime', string='Start Date',
                    help='Calculated Start Date, will be empty if any sprint has no start date.'),
                'date_end': fields.function(_date_end, type='datetime', string='End Date',
                    help='Calculated End Date, will be empty if any sprint has no end date.'),
                'deadline': fields.function(_deadline, type='date', string='Deadline',
                    help='Calculated Deadline, will be empty if any sprint has no deadline.'),
                'expected_hours': fields.function(_expected_hours, type='float',
                    string='Initially Planned Hour(s)', help='Total planned hours calculated '
                    'from sprints.'),
                'effective_hours': fields.function(_effective_hours, type='float',
                    string='Spent Hour(s)', help='Total spent hours calculated '
                    'from sprints.'),
                'remaining_hours': fields.function(_remaining_hours, type='float',
                    string='Remaining Hour(s)', help='Difference between planned '
                    'hours and spent hours.'),
                'progress': fields.function(_progress, type='float', string='Progress (%)',
                    help='Total progress percentage calculated from sprints'),
                'stage_id': fields.many2one('project.task.type', string='Stage', domain="['&', ('fold', '=', False),"
                    " ('project_ids', '=', project_id)]"),
                'state': fields.related('stage_id', 'state', type='selection', selection=STATES,
                    string='State', readonly=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'stage_id': get_default_stage,
                 'product_backlog_id': lambda self, cr, uid, c: c.get('product_backlog_id', False),
                 'project_id': lambda self, cr, uid, c: c.get('project_id', False),
                 }
    
class productBacklog(osv.Model):
    
    _name = 'ccorp.project.scrum.product.backlog'
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculates the product backlog date_end getting the 
        estimated end_date from features related to 
        each product backlog."""
        res = {}
        for id in ids: 
            features = self.browse(cr, uid, id, context=context).feature_ids
            date_end = False
            for feature in features:
                if feature.date_end and feature.state not in ['draft','cancelled']:
                    date = datetime.strptime(feature.date_end, '%Y-%m-%d %H:%M:%S')
                    if not date_end:
                        date_end = date
                    else:
                        if date_end < date:
                            date_end = date 
            if date_end:
                res[id] = datetime.strftime(date_end, '%Y-%m-%d %H:%M:%S')
            else:
                res[id] = date_end
        return res
    
    def _deadline(self, cr, uid, ids, field_name, arg, context=None):
        """Calculates the product backlog deadline getting the 
        estimated end_date from features related to 
        each product backlog."""
        res = {}
        for id in ids: 
            features = self.browse(cr, uid, id, context=context).feature_ids
            deadline = False
            for feature in features:
                if feature.date_end and feature.state not in ['draft','cancelled']:
                    if feature.deadline:
                        date = datetime.strptime(feature.deadline, '%Y-%m-%d')
                        if not deadline:
                            deadline = date
                        else:
                            if deadline < date:
                                deadline = date
            if deadline:
                res[id] = datetime.strftime(deadline, '%Y-%m-%d')
            else:
                res[id] = deadline
        return res
    
    def _expected_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the expected hours from features related 
        to each product backlog."""
        res = {}
        for id in ids:
            features = self.browse(cr, uid, id, context=context).feature_ids
            sum = reduce(lambda result,feature: result+feature.expected_hours,
                         features, 0.0)
            res[id] = sum
        return res
    
    def _effective_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the effective hours from features related 
        to each product backlog."""
        res = {}
        for id in ids:
            features = self.browse(cr, uid, id, context=context).feature_ids
            sum = reduce(lambda result,feature: result+feature.effective_hours,
                         features, 0.0)
            res[id] = sum
        return res
    
    def _remaining_hours(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the difference between expected and effective
        hours from each product backlog."""
        res={}
        backlogs = self.browse(cr, uid, ids, context=context)
        for backlog in backlogs:
            res[backlog.id] = backlog.expected_hours - backlog.effective_hours
        return res
    
    def _progress(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the total progress for each product backlog"""
        res = {}
        for id in ids:
            features = self.browse(cr, uid, id, context=context).feature_ids
            if features:
                sum = reduce(lambda result,feature: result+feature.progress,
                             features, 0.0)
                res[id] = sum/len(features)
            else:
                res[id] = 0.0
        return res
    
    def _set_done(self, cr, uid, ids, context=None):
        project = self.browse(cr, uid, ids[0], context=context).project_id
        for stage in project.type_ids:
            if stage.state == 'cancelled':
                return self.write(cr, uid, ids[0], {'stage_id':stage.id}, context=context)
        raise osv.except_osv(_('Error'), _('There is no done state configured for'
                             ' the project %s') %project.name)
    
    def do_done(self, cr, uid, ids, context=None):
        backlogs = self.browse(cr,uid,ids[0],context=context).release_backlog_ids
        for backlog in backlogs:
            if backlog.state != 'cancelled' and backlog.state != 'done':
                raise osv.except_osv(_('Error'),_('You can not set as done a product backlog if '
                                     'all release backlogs related to it are not cancelled'
                                     ' or done'))
        return self._set_cancel(cr, uid, ids, context=context)
    
    def _set_cancel(self, cr, uid, ids, context=None):
        project = self.browse(cr, uid, ids[0], context=context).project_id
        for stage in project.type_ids:
            if stage.state == 'cancelled':
                return self.write(cr, uid, ids[0], {'stage_id':stage.id}, context=context)
        raise osv.except_osv(_('Error'), _('There is no cancelled state configured for'
                             ' the project %s') %project.name)
    
    def do_cancel(self, cr, uid, ids, context=None):
        backlogs = self.browse(cr,uid,ids[0],context=context).release_backlog_ids
        for backlog in backlogs:
            if backlog.state != 'cancelled' and backlog.state != 'done':
                raise osv.except_osv(_('Error'),_('You can not cancel a product backlog if '
                                     'all release backlogs related to it are not cancelled'
                                     ' or done'))
        return self._set_cancel(cr, uid, ids, context=context)
    
    def onchange_project(self, cr, uid, ids, project_id, stage_id, context=None):
        if project_id:
            type_ids = [x.id for x in self.pool.get('project.project').browse(
                cr, uid, project_id, context=context).type_ids]
            if not stage_id in type_ids: 
                stage = self.get_default_stage_id(cr, uid, project_id, context=context)
                return {
                        'value': {
                                  'stage_id': stage
                                  }
                        }
            else: 
                return {}
        return {
                'value': {
                          'stage_id': self.get_default_stage(cr, uid, context=context)
                          }
                }
    
    def get_default_stage(self, cr ,uid, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,[('state','=','draft')],
            context=context, limit=1)[0]
        if not type:
            raise osv.except_osv(_('Error'),_('There is no ''draft'' state configured.'))
        return type
        
    def get_default_stage_id(self, cr ,uid, project_id, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,
            [('project_ids','=',project_id)], context=context, limit=1)[0]
        return type
            
        
    _columns = {
                'name': fields.char('Product Name', size=128, required=True),
                'project_id': fields.many2one('project.project', string='Project',
                    domain="[('use_tasks','=',True),('state','in',['open','pending']),"
                    "('is_scrum','=',True)]", required=True),
                'user_id': fields.related('project_id', 'user_id', type='many2one',
                    relation='res.users', string='Scrum Master', readonly=True, store=True),
                'member_ids': fields.related('project_id', 'members', type='many2many',
                    relation='res.users', string='Team Members', readonly=True),
                'date_end': fields.function(_date_end, type='datetime',
                    string='End Date', help='Calculated End Date, will be '
                    'empty if any feature has no end date.'),
                'deadline': fields.function(_deadline, type='date',
                    string='Deadline', help='Calculated Deadline, will be empty '
                    'if any feature has no deadline.'),
                'release_backlog_ids': fields.one2many('ccorp.project.scrum.release.backlog',
                    'product_backlog_id', string='Release Backlogs'),
                'feature_ids': fields.one2many('ccorp.project.scrum.feature',
                    'product_backlog_id', string='Features'),
                'expected_hours': fields.function(_expected_hours, type='float',
                    string='Initially Planned Hour(s)', help='Total planned hours '
                    'calculated from features.'),
                'effective_hours': fields.function(_effective_hours, type='float',
                    string='Spent Hour(s)', help='Total spent hours calculated '
                    'from features.'),
                'remaining_hours': fields.function(_remaining_hours, type='float',
                    string='Remaining Hour(s)', help='Difference between planned '
                    'hours and spent hours.'),
                'progress': fields.function(_progress, type='float', string='Progress (%)',
                    help='Total progress percentage calculated from features'),
                'stage_id': fields.many2one('project.task.type', string='Stage', domain="['&', ('fold', '=', False),"
                    " ('project_ids', '=', project_id)]"),
                'state': fields.related('stage_id', 'state', type='selection', selection=STATES, 
                    string='State', readonly=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'stage_id': get_default_stage,
                 }