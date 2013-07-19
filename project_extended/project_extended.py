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

from osv import osv, fields

class project(osv.osv):
    _inherit = 'project.project'
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for project in self.browse(cr, uid, ids, context=context):
            data = []
            proj = project.parent_id
            while proj and proj.parent_id:
                if proj.code != '' and proj.code != False:
                    data.insert(0,(proj.code))
                    proj = proj.parent_id
                    continue
                else:
                    data.insert(0,(proj.name))
                    proj = proj.parent_id
                
                
            
            data.append(project.name)
            data = ' / '.join(data)
            res.append((project.id, data))
        return res

    def _shortcut_name(self, cr, uid, ids,field_name,arg, context=None):
        res ={}
        for m in self.browse(cr,uid,ids,context=context):
            res = self.name_get(cr, uid, ids)
            return dict(res)

        return res
        
    _columns = {
        'shortcut_name': fields.function(_shortcut_name, method=True, string='Project Name', type='char', size=350),
        'ir_sequence_id': fields.many2one('ir.sequence', 'Sequence'),
    }
    
    def create(self, cr, uid, vals, context=None):
        ir_sequence_obj = self.pool.get('ir.sequence')        
        project_id = super(project, self).create(cr, uid, vals, context)
        shortcut_name_dict = self._shortcut_name(cr, uid, [project_id], None, None)
        sequence_name = "Project_" + str(project_id) + " " + shortcut_name_dict[project_id]
        ir_sequence_id = ir_sequence_obj.create(cr, uid, {'name': sequence_name}, context)
        self.write(cr, uid, project_id, {'ir_sequence_id': ir_sequence_id }, context)
        return project_id
    
    def unlink(self, cr, uid, ids, context=None):
        ir_sequence_ids = []
        ir_sequence_obj = self.pool.get('ir.sequence')       
        for proj in self.browse(cr, uid, ids, context=context):
            if proj.ir_sequence_id:
                ir_sequence_ids.append(proj.ir_sequence_id.id)
        res =  super(project, self).unlink(cr, uid, ids, context=context)
        ir_sequence_obj.unlink(cr, uid, ir_sequence_ids, context=context)
        return res
        
class task(osv.osv):
    _inherit = 'project.task'
        
    _columns = {
        'number': fields.char('Number', size=16),
        'project_id': fields.many2one('project.project', 'Project', required=True, ondelete='set null', select="1", track_visibility='onchange'),
    }
    
    def get_number_sequence(self, cr, uid, project_id, context=None):
        ir_sequence_obj = self.pool.get('ir.sequence')
        project_obj = self.pool.get('project.project')        
        project = project_obj.browse(cr, uid, project_id, context)
        return ir_sequence_obj.next_by_id(cr, uid, project.ir_sequence_id.id, context)
        
    def create(self, cr, uid, vals, context={}):
        if 'number' not in vals or vals['number']== None or vals['number'] == '':
            vals.update({'number': self.get_number_sequence(cr, uid, vals['project_id'], context)})
        return super(task, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'project_id' in vals:
            vals.update({'number': self.get_number_sequence(cr, uid, vals['project_id'], context)})
        return super(task, self).write(cr, uid, ids, vals, context)
