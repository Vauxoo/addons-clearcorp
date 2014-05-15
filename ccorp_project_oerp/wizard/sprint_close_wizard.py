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

class SprintCloseWizard(osv.TransientModel):
    
    _name = 'ccorp.project.oerp.sprint.close.wizard'
    
    def close_sprint(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        closing = wizard.closing_sprint_id
        opening = wizard.opening_sprint_id
        
        try:
            task_ids = []
            for task in closing.task_ids:
                if task.state in ['open','pending','draft']:
                    task_ids.append(task.id)
                    task.write({'sprint_id': False}, context=context)
                    
            feature_ids = []
            for feature in closing.feature_ids:
                if feature.state not in ['cancelled','done']:
                    feature_ids.append(feature.id)
            opening.write({
                           'desirable_task_ids': [[6,0,task_ids]],
                           'feature_ids': [[6,0,feature_ids]],
                           }, context=context)
            
            closing.set_done(context=context)
            
            return {
                    'name': 'Sprints',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'ccorp.project.scrum.sprint',
                    'context': context,
                    'res_id': opening.id,
                    'type': 'ir.actions.act_window',
                }
        
        except:
            raise osv.except_osv(_('Error'),_('An error occurred while closing the sprint.'))
    
    _columns = {
                'closing_sprint_id': fields.many2one('ccorp.project.scrum.sprint', string='Closing Sprint',
                    required=True, domain="[('state','in',['open','pending'])]"),
                'opening_sprint_id': fields.many2one('ccorp.project.scrum.sprint', string='Opening Sprint',
                    required=True, domain="[('state','in',['draft','close'])]"),
                }