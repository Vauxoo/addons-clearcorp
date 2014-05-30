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

# Mapping between task priority and
# feature priority
PRIORITY = {
            5: '4',
            4: '3',
            3: '2',
            2: '1',
            1: '0',
            }


class TaskCreateWizard(osv.TransientModel):
    
    _name = 'ccorp.project.oerp.task.create.wizard'
    
    def create_tasks(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        sprint = wizard.sprint_id
        features = wizard.sprint_id.feature_ids
        
        desirables = []
        for feature in features:
            try:
                cr.execute('''SELECT string_agg(types.name,', ') AS name,
 types.sequence,
 SUM(types.expected_hours) AS expected_hours
FROM (SELECT types.id,
 types.sequence,
 types.name,
 hours.expected_hours
FROM ccorp_project_oerp_feature_hours AS hours,
 ccorp_project_oerp_work_type AS types
WHERE hours.feature_id = %s
AND hours.phase_id = %s
AND hours.work_type_id = types.id) AS types
GROUP BY types.sequence
ORDER BY types.sequence ASC;''', (feature.id, sprint.phase_id.id))
                
                previous_id = False
                for sequence in cr.dictfetchall():
                    number = sequence.get('sequence')
                    values = {
                              'name': feature.code + ' ' + feature.name + \
                              ' ' + sequence.get('name'),
                              'project_id': sprint.project_id.id,
                              'product_backlog_id': sprint.product_backlog_id.id,
                              'release_backlog_id': sprint.release_backlog_id.id,
                              'sprint_id': False,
                              'feature_id': feature.id,
                              'description': feature.description,
                              'planned_hours': sequence.get('expected_hours'),
                              'remaining_hours': sequence.get('expected_hours'),
                              'priority': PRIORITY[feature.priority],
                              'phase_id': sprint.phase_id.id,
                              'date_deadline': sprint.deadline,
                              'date_start': sprint.date_start,
                              'sequence': number,
                              }
                    
                    cr.execute('''SELECT types.id,
 hours.expected_hours,
 hours.phase_id
FROM ccorp_project_oerp_feature_hours AS hours,
 ccorp_project_oerp_work_type AS types
WHERE hours.feature_id = %s
AND hours.work_type_id = types.id
AND types.sequence = %s;''', (feature.id, number,))
                    
                    vals = []
                    for row in cr.dictfetchall():
                        vals.append([0,0,{
                                          'phase_id': row.get('phase_id'),
                                          'work_type_id': row.get('id'),
                                          'expected_hours': row.get('expected_hours'),
                                          }])
                    
                    values['task_hour_ids'] = vals
                    
                    if sprint.phase_id.user_id:
                        values['user_id'] = sprint.phase_id.user_id.id
                    
                    task_obj = self.pool.get('project.task')
                    task_id = task_obj.create(cr, uid, values, context=context)
                    desirables.append(task_id)
                    
                    if previous_id:
                        values = {'previous_task_ids': [[6,0,[previous_id]]]}
                        task_obj.write(cr, uid, task_id, values, context=context)
                        values = {'next_task_ids': [[6,0,[task_id]]]}
                        task_obj.write(cr, uid, previous_id, values, context=context)
                    
                    previous_id = task_id
                
            except:
                raise osv.except_osv(_('Error'),_('An error occurred while creating the tasks. '
                                                  'Please contact your system administrator.'))
            
        sprint_obj = self.pool.get('ccorp.project.scrum.sprint')
        for desirable in desirables:
            sprint_obj.write(cr, uid, sprint.id,
                             {
                              'desirable_task_ids': [[4,desirable]],
                              })
            
        return {
                'name': 'Sprints',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ccorp.project.scrum.sprint',
                'context': context,
                'res_id': sprint.id,
                'type': 'ir.actions.act_window',
                }
    
    _columns = {
                'sprint_id': fields.many2one('ccorp.project.scrum.sprint', string='Sprint',
                    required = True, domain="[('state','=','open')]"),
                }
    
    _defaults = {
                 'sprint_id': lambda slf, cr, uid, ctx: ctx.get('sprint_id', False),
                 }