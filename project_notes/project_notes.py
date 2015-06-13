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

from openerp import models, fields


class Project(models.Model):

    _inherit = 'project.project'

    notes = fields.Text('Notes')
    project_objective_ids = fields.One2many(
        'project.notes.objetives',
        'project_id',
        string='Indicators'
    )


class Project_notes_objetives(models.Model):
    """Objectives"""

    _name = 'project.notes.objetives'
    _description = __doc__

    project_id = fields.Many2one('project.project', string='Projects')
    justification = fields.Text('Justification')
    objetive = fields.Text(string='Objective')
    indicator = fields.Char(string='Indicator')
    target_value = fields.Char(string='Target Value')
    result_obtained = fields.Char(string='Result Obtained')
