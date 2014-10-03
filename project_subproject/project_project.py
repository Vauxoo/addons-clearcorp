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

from openerp import models, fields, api

class Project(models.Model):

    _inherit = 'project.project'

    @api.one
    @api.returns('project.project')
    def _get_parent_project_id(self):
        # Check if the project has parent_id
        if self.parent_id:
            parent_project = self.search([('analytic_account_id','=', self.parent_id.id)], limit=1)
            return parent_project
        else:
            return self.env['project.project']

    @api.model
    def create(self, values):
        project = super(Project, self).create(values)
        project.parent_project_id = project._get_parent_project_id()
        return project

    @api.multi
    def write(self, values):
        if 'parent_id' in values:
            parent_project_id = self.search(
                [('analytic_account_id','=', values['parent_id'])], limit=1)
            if parent_project_id:
                values['parent_project_id'] = parent_project_id.id
            else:
                values['parent_project_id'] = False
        return super(Project, self).write(values)

    @api.one
    @api.depends('subproject_ids')
    def _compute_subproject_count(self):
        self.subproject_count = len(self.subproject_ids.ids)

    parent_project_id = fields.Many2one('project.project', string='Parent Project', readonly=True)
    subproject_ids = fields.One2many('project.project','parent_project_id', string='Sub-Projects', readonly=True)
    subproject_count = fields.Integer(string='Sub-projects Quantity', compute='_compute_subproject_count', store=True)