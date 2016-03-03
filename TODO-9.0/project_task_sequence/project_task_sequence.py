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

class project(osv.Model):
    _inherit = 'project.project'
    
    _columns = {
        'task_sequence_id':       fields.many2one('ir.sequence', 'Task Sequence',domain=[('code','=','project.project')]),
                }
    
    def create(self, cr, uid, vals, context=None):
        project_id = super(project, self).create(cr, uid, vals, context)
        if 'task_sequence_id' not in vals.keys() or not vals['task_sequence_id']:
            ir_sequence_obj = self.pool.get('ir.sequence')
            sequence_name = "Project " + str(project_id) + " " + vals['name']
            task_sequence_id = ir_sequence_obj.create(cr, uid, {'name': sequence_name, 'code':'project.project'}, context)
            self.write(cr, uid, project_id, {'task_sequence_id': task_sequence_id }, context=context)
        return project_id
    
    def write(self, cr, uid, id, vals, context=None):
        project_id = super(project, self).write(cr, uid, id, vals, context=context)
        if 'task_sequence_id' in vals.keys() and not vals['task_sequence_id']:
            ir_sequence_obj = self.pool.get('ir.sequence')
            sequence_name = "Project " + str(project_id) + " " + vals['name']
            task_sequence_id = ir_sequence_obj.create(cr, uid, {'name': sequence_name, 'code':'project.project'}, context)
            self.write(cr, uid, project_id, {'task_sequence_id': task_sequence_id }, context=context)
        return project_id
    
    def unlink(self, cr, uid, ids, context=None):
        task_sequence_ids = []
        ir_sequence_obj = self.pool.get('ir.sequence')       
        for proj in self.browse(cr, uid, ids, context=context):
            if proj.task_sequence_id and not self.search(cr,uid,[('task_sequence_id','=',proj.task_sequence_id.id),('id','<>',proj.id)],context=context):
                task_sequence_ids.append(proj.task_sequence_id.id)
        res = super(project, self).unlink(cr, uid, ids, context=context)
        ir_sequence_obj.unlink(cr, uid, task_sequence_ids, context=context)
        return res
    
class task(osv.Model):
    _inherit = 'project.task'
    
    _columns = {
        'number': fields.char('Number', size=32),
                }
    def get_number_sequence(self, cr, uid, project_id, context=None):
        ir_sequence_obj = self.pool.get('ir.sequence')
        project_obj = self.pool.get('project.project')
        project = project_obj.browse(cr, uid, project_id, context)
        return ir_sequence_obj.next_by_id(cr, uid, project.task_sequence_id.id, context)
    
    def create(self, cr, uid, vals, context={}):
        if 'number' not in vals or vals['number'] == None or vals['number'] == '':
            vals.update({'number': self.get_number_sequence(cr, uid, vals['project_id'], context)})
        return super(task, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'project_id' in vals:
            vals.update({'number': self.get_number_sequence(cr, uid, vals['project_id'], context)})
        return super(task, self).write(cr, uid, ids, vals, context)
