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
from datetime import datetime

# Mapping between task priority and
# feature priority
PRIORITY = {
            1: '3',
            2: '2',
            3: '1',
            4: '0',
            }

class featureType(osv.Model):
    
    _name = 'project.scrum.feature.type'
    
    _columns = {
                'code': fields.char('Code', size=16, required=True),
                'name': fields.char('Type Name', size=128, required=True),
                }
    
    def name_get(self, cr, uid, ids, context=None):
        res =[]
        for r in self.read(cr, uid, ids, ['code', 'name'], context=context):
            name = '%s - %s' %(r['code'],r['name'])
            res.append((r['id'], name))
        return res
    
# TODO: manage states
class feature(osv.Model):
    
    _name = 'project.scrum.feature'
    
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
                                        ('feature_id','=',id)],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            date_start = False
            for task in tasks:
                if not task.date_start:
                    date_start = False
                    break
                else:
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
                                        ('feature_id','=',id)],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            date_end = False
            for task in tasks:
                if not task.date_end:
                    date_end = False
                    break
                else:
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
                                        ('feature_id','=',id)],
                                       context=context)
            tasks = task_obj.browse(cr,uid,task_ids,context=context)
            deadline = False
            for task in tasks:
                if not task.date_deadline:
                    deadline = False
                    break
                else:
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
    
    def onchange_product_backlog(self, cr, uid, ids, product_id, release_id, context=None):
        if product_id and release_id:
            backlog = self.pool.get('project.scrum.release.backlog').browse(
                cr, uid, release_id, context=context)
            if product_id == backlog.product_backlog_id.id:
                return {}
        return {
                'value': {'release_backlog_id': False},
                }
    
    def set_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)
    
    def set_approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approved'}, context=context)
    
    def set_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
    
    def set_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)
    
    _columns = {
                'name': fields.char('Feature Name', size=128, required=True),
                'code': fields.char('Code', size=16),
                'product_backlog_id': fields.many2one('project.scrum.product.backlog',
                    string='Product Backlog', required=True, domain="['|',('state','=','open'),"
                    "('state','=','pending')]"),
                'release_backlog_id': fields.many2one('project.scrum.release.backlog',
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
                'type_id': fields.many2one('project.scrum.feature.type', string='Type'),
                'priority': fields.selection([(1,'Low'),(2,'Medium'),(3,'High'),
                    (4,'Very High')], string='Priority', required=True),
                'sprint_ids': fields.many2many(
                    'project.scrum.sprint', readonly=True, 
                    rel='project_scrum_sprint_backlog',
                    help='Sprints in which the feature has been used.'),
                'date_start': fields.function(_date_start, type='datetime', string='Start Date'),
                'date_end': fields.function(_date_end, type='datetime', string='End Date'),
                'deadline': fields.function(_deadline, type='date', string='Deadline'),
                'expected_hours': fields.float('Initially Planned Hour(s)',
                    help='Total planned hours for the development of '
                    'this feature.\nRecommended values are:\n 1h, 2h, 4h,'
                    ' or 8h', required=True),
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
    # TODO: generate sequence code
    _defaults = {
                 'code': 'PRJ001',
                 'priority': 2,
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
    #def name_search(self, cr, uid, name, args=[], operator='ilike', context=None, limit=80):
        ids = []
        if name:
            ids = self.search(cr, uid,
                              ['|',('code',operator,name),
                               ('name',operator,name)] + args,
                              limit=limit, context=context)
        else:
            ids  = self.search(cr, uid, args, limit=limit, context=context)
        
        return self.name_get(cr, uid, ids, context=context)
    
# TODO: reevaluate tasks when do_reopen is called
class sprint(osv.Model):
    
    _name = 'project.scrum.sprint'
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate End date as the highest End Date from
        tasks related to this sprint"""
        res = {}
        for id in ids:
            tasks = self.browse(cr, uid, id, context=context).task_ids
            date_end = False
            for task in tasks:
                if task.date_end:
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
    
    def onchange_product_backlog(self, cr, uid, ids, product_id, release_id, context=None):
        vals = {}
        if product_id:
            backlog = self.pool.get('project.scrum.product.backlog').browse(
                    cr,uid,product_id,context=context)
            vals['project_id'] = backlog.project_id.id
            if release_id:
                backlog = self.pool.get('project.scrum.release.backlog').browse(
                    cr,uid,release_id,context=context)
                if not product_id == backlog.product_backlog_id.id:
                    vals['release_backlog_id'] = False
        else:
            vals['project_id'] = False
            vals['release_backlog_id'] = False
        return {'value': vals}
        
    def onchange_release_backlog(self, cr, uid, ids, release_id, context=None):
        return {
                'value': {'feature_ids': False},
                }
    
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
    
    def _get_default_project_id(self, cr, uid, context={}):
        proj = False
        if context:
            proj = context.get('default_project_id', False)
        if type(proj) is int:
            return [proj]
        return proj
    
    def get_default_stage(self, cr ,uid, context=None):
        project_id = self._get_default_project_id(cr, uid, context=context)
        type_obj = self.pool.get('project.task.type')
        if project_id:
            type = type_obj.search(cr,uid,
                [('project_ids','=',project_id)], context=context, limit=1)[0]
            return type
        else:
            type = type_obj.search(cr,uid,
                [('case_default','=',True)], context=context, limit=1)[0]
            return type
        
    def get_default_stage_id(self, cr ,uid, project_id, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,
            [('project_ids','=',project_id)], context=context, limit=1)[0]
        return type
    
    def set_open(self, cr, uid, ids, context=None):
        task_ids = [x.id for x in self.browse(cr, uid, ids[0], context=context).task_ids]
        res = task_obj = self.pool.get('project.task').do_reopen(cr,uid,task_ids,context=context)
        if not res:
                raise osv.except_osv('Error','This sprint cannot be opened. Please'
                                     'check if all tasks can be reevaluated normally.')
        return self.write(cr, uid, ids, {'state':'open'}, context=context)
    
    def set_close(self, cr, uid, ids, context=None):
        tasks = self.browse(cr, uid, ids[0], context=context).task_ids
        task_obj = self.pool.get('project.task')
        for task in tasks:
            res = task_obj.action_close(cr,uid,[task.id],context=context)
            if not res:
                raise osv.except_osv('Error','This sprint cannot be closed. Please'
                                     'check if all tasks can be closed normally.')
        return self.write(cr, uid, ids, {'state':'close'}, context=context)
    
    def set_pending(self, cr, uid, ids, context=None):
        task_ids = [x.id for x in self.browse(cr, uid, ids[0], context=context).task_ids]
        res = task_obj = self.pool.get('project.task').do_pending(cr,uid,task_ids,context=context)
        if not res:
                raise osv.except_osv('Error','This sprint cannot be set as pending. Please'
                                     'check if all tasks can be changed to pending normally.')
        return self.write(cr, uid, ids, {'state':'pending'}, context=context)
    
    def set_cancel(self, cr, uid, ids, context=None):
        task_ids = [x.id for x in self.browse(cr, uid, ids[0], context=context).task_ids]
        res = task_obj = self.pool.get('project.task').do_cancel(cr,uid,task_ids,context=context)
        if not res:
                raise osv.except_osv('Error','This sprint cannot be cancelled. Please'
                                     'check if all tasks can be cancelled normally.')
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)
    
    def tasks_from_features(self, cr, uid, ids, context=None):
        sprint = self.browse(cr, uid, ids[0], context=context)
        if sprint.task_from_features:
            raise osv.except_osv('Error','All task were created before.')
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
                      'date_deadline': sprint.deadline,
                      'priority': PRIORITY[feature.priority],
                      'description': feature.description,
                      'name': 'Task for: ' + feature.code + '' + feature.name,
                      }
            task_obj.create(cr, uid, values, context=context)
        self.write(cr, uid, ids[0], {'task_from_features': True}, context=context)
        return True
    
    def set_features_done(self, cr, uid, ids, context=None):
        sprint = self.browse(cr, uid, ids[0], context=context)
        for feature in sprint.feature_ids:
            feature.write({'state': 'done'}, context=context)
        return True
    
    def _check_deadline(self, cr, uid, ids, context=None):
        sprints =self.browse(cr, uid, ids, context=context)
        for sprint in sprints:
            date_start = datetime.strptime(sprint.date_start, '%Y-%m-%d %H:%M:%S')
            deadline = datetime.strptime(sprint.deadline, '%Y-%m-%d')
            if deadline < date_start:
                return False
        return True
    
    _columns = {
                'name': fields.char('Sprint Name', size=128, required=True),
                'product_backlog_id': fields.many2one('project.scrum.product.backlog',
                    string='Product Backlog', domain="['|',('state','=','open'),"
                    "('state','=','pending')]", required=True),
                'release_backlog_id': fields.many2one('project.scrum.release.backlog',
                    required=True, string='Release Backlog', domain="[('product_backlog_id','=',product_backlog_id),"
                    "'|',('state','=','open'),('state','=','pending')]"),
                'project_id': fields.related('release_backlog_id','product_backlog_id','project_id',
                    relation='project.project', type='many2one', string='Project', store=True, readonly=True),
                'user_id': fields.related('release_backlog_id','product_backlog_id','project_id', 'user_id',
                    relation='res.users', type='many2one', string='Scrum Master', store=True),
                'member_ids': fields.related('release_backlog_id','product_backlog_id','project_id', 'members',
                    relation='res.users', type='many2many', string='Team Members', readonly=True),
                'task_ids': fields.one2many('project.task', 'sprint_id', string='Tasks'),
                'feature_ids': fields.many2many('project.scrum.feature', rel='project_scrum_sprint_backlog',
                    string='Features', help='Features to be developed in this sprint', 
                    domain="[('state','=','open'),('release_backlog_id','=',release_backlog_id),"
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
                'task_from_features': fields.boolean('Tasks from features', readonly=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'date_start': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
                 'deadline': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d'),
                 'stage_id': get_default_stage,
                 'product_backlog_id': lambda self, cr, uid, c: c.get('product_backlog_id', False),
                 'release_backlog_id': lambda self, cr, uid, c: c.get('release_backlog_id', False),
                 }
    
    _constraints = [(_check_deadline, 'Deadline must be greater than Start Date',['Start Date','Deadline'])]
    
# TODO: add work hours + date to task date_end
# TODO: create tasks from features
# TODO: fix domain in user_id
class task(osv.Model):
    
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
    
    def onchange_product(self, cr, uid, ids, product_id, release_id, context=None):
        value = {
                 'release_backlog_id': False,
                 }
        if product_id:
            product_obj = self.pool.get('project.scrum.release.backlog')
            product = product_obj.browse(cr,uid,product_id,context=context)
            if release_id:
                if release_id in product.release_backlog_ids:
                    return {}
        return {
                'value': value
                }
    
    def onchange_release(self, cr, uid, ids, release_id, sprint_id, context=None):
        value = {
                 'sprint_id': False,
                 }
        if release_id:
            release_obj = self.pool.get('project.scrum.release.backlog')
            release = release_obj.browse(cr,uid,release_id,context=context)
            if sprint_id:
                if sprint_id in release.sprint_ids:
                    return {}
        return {
                'value': value
                }
    
    def onchange_sprint(self, cr, uid, ids, sprint_id, feature_id, user_id, context=None):
        value = {
                 'date_deadline': False,
                 }
        domain = {
                  'user_id': []
                  }
        if sprint_id:
            sprint_obj = self.pool.get('project.scrum.sprint')
            sprint = sprint_obj.browse(cr,uid,sprint_id,context=context)
            value['date_deadline'] = sprint.deadline
            member_ids = [x.id for x in sprint.member_ids]
            domain['user_id'] = [('id','in',member_ids)]
            if feature_id:
                if not feature_id in sprint.feature_ids:
                    value['feature_id'] = False
            if user_id:
                if not user_id in sprint.member_ids:
                    value['user_id'] = False
        else:
            value['feature_id'] = False
            value['user_id'] = False
        return {
                'domain': domain,
                'value': value,
                }
        
    def onchange_feature(self, cr, uid, ids, feature_id, context=None):
        if feature_id:
            feature = self.pool.get('project.scrum.feature').browse(
                cr,uid,feature_id,context=context)
            return {
                    'value': {
                              'planned_hours': feature.expected_hours,
                              'priority': PRIORITY[feature.priority],
                              }
                    }
        return {
                'value': {
                          'planned_hours': False,
                          'priority': '2',
                          }
                }
    
    _columns = {
                'product_backlog_id': fields.many2one('project.scrum.product.backlog', string='Product Backlog',
                    domain="[('project_id','=',project_id),('state','=','open')]"),
                'release_backlog_id': fields.many2one('project.scrum.release.backlog', string='Release Backlog',
                    domain="[('product_backlog_id','=',product_backlog_id),('state','=','open')]"),
                'sprint_id': fields.many2one('project.scrum.sprint', string='Sprint',
                    domain ="[('release_backlog_id','=',release_backlog_id),('state','=','open')]"),
                'feature_id': fields.many2one('project.scrum.feature', string='Feature',
                    domain="[('sprint_ids','=',sprint_id),('state','=','open')]"),
                }
    
    _defaults = {
                 'date_start': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
                 'date_end': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
                 }
    
class releaseBacklog(osv.Model):
    
    _name = 'project.scrum.release.backlog'
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculate the end date from sprints related to 
        each backlog"""
        res = {}
        for id in ids:
            sprints = self.browse(cr, uid, id, context=context).sprint_ids
            date_end = False
            for sprint in sprints:
                if not sprint.date_end:
                    date_end = False
                    break
                else:
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
                if not sprint.date_start:
                    date_start = False
                    break
                else:
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
                if not sprint.deadline:
                    deadline = False
                    break
                else:
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
            project_id = self.pool.get('project.scrum.product.backlog').browse(
                cr,uid,backlog_id,context=context).project_id.id
            value['project_id'] = project_id
        return {
                'value': value
                }
    
    '''def set_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)
    
    def set_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'close'}, context=context)
    
    def set_pending(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'pending'}, context=context)
    
    def set_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)'''
    
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
    
    def _get_default_project_id(self, cr, uid, context={}):
        proj = False
        if context:
            proj = context.get('default_project_id', False)
        if type(proj) is int:
            return [proj]
        return proj
    
    def get_default_stage(self, cr ,uid, context=None):
        project_id = self._get_default_project_id(cr, uid, context=context)
        type_obj = self.pool.get('project.task.type')
        if project_id:
            type = type_obj.search(cr,uid,
                [('project_ids','=',project_id)], context=context, limit=1)[0]
            return type
        else:
            type = type_obj.search(cr,uid,
                [('case_default','=',True)], context=context, limit=1)[0]
            return type
        
    def get_default_stage_id(self, cr ,uid, project_id, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,
            [('project_ids','=',project_id)], context=context, limit=1)[0]
        return type
    
    _columns = {
                'name': fields.char('Release Name', size=128, required=True),
                'product_backlog_id': fields.many2one('project.scrum.product.backlog',
                    string= 'Product Backlog', required=True, domain="[('state','in',['open','pending'])]"),
                'project_id': fields.related('product_backlog_id', 'project_id', type='many2one',
                    relation='project.project', string='Project', readonly=True, store=True),
                'user_id': fields.related('product_backlog_id', 'project_id','user_id', type='many2one',
                    relation='res.users', string='Project', readonly=True, store=True),
                'feature_ids': fields.one2many('project.scrum.feature','release_backlog_id',
                    string='Features'),
                'sprint_ids': fields.one2many('project.scrum.sprint', 'release_backlog_id',
                    string='Sprints'),
                'date_start': fields.function(_date_start, type='datetime', string='Start Date',
                    help='Calculated Start Date, will be empty if any sprint has no start date.'),
                'date_end': fields.function(_date_end, type='datetime', string='End Date',
                    help='Calculated End Date, will be empty if any sprint has no end date.'),
                'deadline': fields.function(_deadline, type='date', string='Deadline',
                    help='Calculated Deadline, will be empty if any sprint has no end date.'),
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
                'state': fields.related('stage_id', 'state', type='selection', string='State', readonly=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'stage_id': get_default_stage,
                 'product_backlog_id': lambda self, cr, uid, c: c.get('product_backlog_id', False),
                 'project_id': lambda self, cr, uid, c: c.get('project_id', False),
                 }
    
# TODO: create kanban view
# TODO: Change state of related items when state changes
class productBacklog(osv.Model):
    
    _name = 'project.scrum.product.backlog'
    
    def _date_end(self, cr, uid, ids, field_name, arg, context=None):
        """Calculates the product backlog date_end getting the 
        estimated end_date from features related to 
        each product backlog."""
        res = {}
        for id in ids: 
            features = self.browse(cr, uid, id, context=context).feature_ids
            date_end = False
            for feature in features:
                if not feature.date_end:
                    date_end = False
                    break
                else:
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
                if not feature.deadline:
                    deadline = False
                    break
                else:
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
    
    '''def set_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)
    
    def set_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'close'}, context=context)
    
    def set_pending(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'pending'}, context=context)
    
    def set_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)'''
    
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
    
    def _get_default_project_id(self, cr, uid, context={}):
        proj = context.get('default_project_id', False)
        if type(proj) is int:
            return [proj]
        return proj
    
    def get_default_stage(self, cr ,uid, context=None):
        project_id = self._get_default_project_id(cr, uid, context=context)
        type_obj = self.pool.get('project.task.type')
        if project_id:
            type = type_obj.search(cr,uid,
                [('project_ids','=',project_id)], context=context, limit=1)[0]
            return type
        else:
            type = type_obj.search(cr,uid,
                [('case_default','=',True)], context=context, limit=1)[0]
            return type
        
    def get_default_stage_id(self, cr ,uid, project_id, context=None):
        type_obj = self.pool.get('project.task.type')
        type = type_obj.search(cr,uid,
            [('project_ids','=',project_id)], context=context, limit=1)[0]
        return type
            
        
    _columns = {
                'name': fields.char('Product Name', size=128, required=True),
                'project_id': fields.many2one('project.project', string='Project',
                    domain="[('use_tasks','=',True),('state','in',['open','pending'])]", required=True),
                'user_id': fields.related('project_id', 'user_id', type='many2one',
                    relation='res.users', string='Scrum Master', readonly=True, store=True),
                'member_ids': fields.related('project_id', 'members', type='many2many',
                    relation='res.users', string='Team Members', readonly=True),
                'date_end': fields.function(_date_end, type='datetime',
                    string='End Date', help='Calculated End Date, will be '
                    'empty if any feature has no end date.'),
                'deadline': fields.function(_deadline, type='date',
                    string='Deadline', help='Calculated Deadline, will be empty '
                    'if any feature has no end date.'),
                'release_backlog_ids': fields.one2many('project.scrum.release.backlog',
                    'product_backlog_id', string='Release Backlogs'),
                'feature_ids': fields.one2many('project.scrum.feature',
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
                'state': fields.related('stage_id', 'state', type='selection', string='State', readonly=True),
                'color': fields.integer('Color Index'),
                }
    
    _defaults = {
                 'stage_id': get_default_stage,
                 }