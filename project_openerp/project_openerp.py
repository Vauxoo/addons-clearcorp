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

class TaskType(osv.Model):
    
    _name = 'project.oerp.task.type'
    
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
                'task_type_ids': fields.one2many('project.oerp.task.type', 'phase_id', string='Task Types'),
                }