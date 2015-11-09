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
from dateutil.relativedelta import relativedelta
from datetime import datetime

_TASK_STATE = [('draft', 'New'), ('open', 'In Progress'), ('pending', 'Pending'), ('ready', 'Ready'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class project_task_type(osv.Model):
    
    _inherit = 'project.task.type'

    _columns = {
        'state': fields.selection(_TASK_STATE, 'Related Status', required=True),
        'task_type':fields.many2one('task.type', string='Task Type'),
    }
    
    def mark_done(self, cr, uid, ids, context=None):
        values = {
            'state': 'done',
            'name': _('Done'),
            'readonly':'True',
        }
        self.write(cr, uid, ids, values, context=context)
        return True

    _defaults = {
        'state': 'open',
        'fold': False,
        'case_default': False,
     }
    
class task(osv.Model):
    _inherit = 'project.task'
    
    _columns = {
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
        }
    
    def set_kanban_state_blocked(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'kanban_state': 'blocked'}, context=context)

    def set_kanban_state_normal(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'kanban_state': 'normal'}, context=context)

    def set_kanban_state_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'kanban_state': 'done'}, context=context)
        return False