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

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import date

_ISSUE_STATE = [('draft', 'New'), ('qualify', 'Qualify'), ('open', 'In Progress'), ('pending', 'Pending'), ('ready', 'Ready'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class project_issue_type(models.Model):
    _name = 'project.issue.type'
    _description = 'Issue Stage'
    _order = 'sequence'
    
    name = fields.Char('Stage Name', required=True, translate=True)
    description= fields.Text('Description')
    sequence= fields.Integer('Sequence')
    case_default= fields.Boolean('Default for New Projects',
                        help="If you check this field, this stage will be proposed by default on each new project. It will not assign this stage to existing projects.")
    fold= fields.Boolean('Folded in Kanban View', help='This stage is folded in the kanban view when'
                               'there are no records in that stage to display.')
    state= fields.Selection(_ISSUE_STATE, 'Related Status', required=True)
    
    _defaults = {
        'state': 'open',
                }
    
class project_issue(models.Model):
    
    _inherit = 'project.issue'
    
    
    stage_id = fields.Many2one ('project.issue.type', track_visibility='onchange', select=True, copy=False)

        
