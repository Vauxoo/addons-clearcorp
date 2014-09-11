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

class PhaseCreateWizard(osv.TransientModel):
    
    _name = 'ccorp.project.oerp.phase.create.wizard'
    
    def create_phase(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        
        values = {
                  'name': wizard.work_type_template_id.name,
                  'project_id': wizard.project_id.id,
                  'product_backlog_id': wizard.product_backlog_id.id,
                  'duration': wizard.duration,
                  'product_uom': wizard.product_uom.id,
                  }
        
        work_type_ids = []
        for work_type in wizard.work_type_template_id.work_type_mapping_ids:
            vals = {
                    'name': work_type.name,
                    'sequence': work_type.sequence,
                    'column_number': work_type.column_number,
                    }
            work_type_ids.append([0,False,vals])
            
        values['work_type_ids'] = work_type_ids
            
        phase_obj = self.pool.get('project.phase')
        phase_id = phase_obj.create(cr, uid, values, context=context)
        return {
                'name': 'Project Phases',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'project.phase',
                'context': context,
                'res_id': phase_id,
                'type': 'ir.actions.act_window',
                }
    
    _columns = {
                'work_type_template_id': fields.many2one('ccorp.project.oerp.work.type.template', string='Work Type Template',
                    required=True),
                'project_id': fields.many2one('project.project', string='Project', required=True,
                    domain="[('is_scrum','=',True)]"),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog', string='Product Backlog',
                    required=True, domain="[('project_id','=',project_id)]"),
                'duration': fields.float('Duration', required=True),
                'product_uom': fields.many2one('product.uom', string='Unit of Measure', required=True),
                }