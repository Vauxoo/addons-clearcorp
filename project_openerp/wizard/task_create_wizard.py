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
    
    _name = 'project.oerp.task.create.wizard'
    
    def create_tasks(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        sprint = wizard.sprint_id
        features = wizard.sprint_id.feature_ids
        
        for feature in features:
            if sprint.task_from_features:
                raise osv.except_osv(_('Error'),_('All task were created before.'))
            try:
                cr.execute('''SELECT types.name AS name,
planned.expected_hours AS expected_hours,
types.sequence
FROM (SELECT string_agg(name,', ') AS name,
 sequence
FROM project_oerp_work_type
GROUP BY sequence) AS types, 
(SELECT SUM(hours.expected_hours) AS expected_hours,
 types.sequence
FROM project_oerp_work_type AS types,
 project_oerp_feature_hours AS hours
WHERE types.id = hours.work_type_id
AND hours.feature_id = %d
GROUP BY types.sequence) AS planned
WHERE types.sequence = planned.sequence
ORDER BY types.sequence ASC;''' % feature.id)
                
                previous_id = False
                for row in cr.dictfetchall():
                    values = {
                                  'name': _('Task for: %s') % 
                                  (feature.code + ' ' + feature.name + \
                                   ' ' + row.get('name')),
                                  'project_id': sprint.project_id.id,
                                  'product_backlog_id': sprint.product_backlog_id.id,
                                  'release_backlog_id': sprint.release_backlog_id.id,
                                  'sprint_id': sprint.id,
                                  'feature_id': feature.id,
                                  'description': feature.description,
                                  'planned_hours': row.get('expected_hours'),
                                  'remaining_hours': row.get('expected_hours'),
                                  'priority': PRIORITY[feature.priority],
                                  'phase_id': sprint.phase_id.id,
                                  'date_deadline': sprint.deadline,
                                  'date_start': sprint.date_start,
                                  }
                    
                    task_obj = self.pool.get('project.task')
                    task_id = task_obj.create(cr, uid, values, context=context)
                    
                    if previous_id:
                        values = {'previous_task_ids': [[6,0,[previous_id]]]}
                        task_obj.write(cr, uid, task_id, values, context=context)
                    
                    previous_id = task_id
                    
                sprint_obj = self.pool.get('project.scrum.sprint')
                sprint_obj.write(cr, uid, sprint.id, {'task_from_features': True})
                
            except:
                osv.except_osv(_('Error'),_('An error occurred while creating the tasks. '
                                            'Please contact your system administrator.'))
        return {
                'name': 'Sprints',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.scrum.sprint',
                'context': context,
                'res_id': sprint.id,
                'type': 'ir.actions.act_window',
                }
    
    _columns = {
                'sprint_id': fields.many2one('project.scrum.sprint', string='Sprint',
                    required = True, domain="[('state','=','open')]"),
                }
    
    _defaults = {
                 'sprint_id': lambda slf, cr, uid, ctx: ctx.get('sprint_id', False),
                 }