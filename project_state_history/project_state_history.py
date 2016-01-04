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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProjectStateHistory(models.Model):

    _name = 'project.state.history'

    @api.one
    @api.depends('date', 'project_id')
    def _compute_value(self):
        last_history = self.search([
            ('project_id', '=', self.project_id.id),
            ('date', '<', self.date)], order='date DESC', limit=1)
        if last_history:
            now = datetime.strptime(self.date,
                                    DEFAULT_SERVER_DATETIME_FORMAT)
            last = datetime.strptime(last_history.date,
                                     DEFAULT_SERVER_DATETIME_FORMAT)
            self.value = (((now - last).days * 24.0 * 60.0) +
                          (now - last).seconds / 60.0) / 60.0
        else:
            self.value = 0.0

    state_from = fields.Selection([
        ('template', 'Template'), ('draft', 'New'), ('open', 'In Progress'),
        ('cancelled', 'Cancelled'), ('pending', 'Pending'),
        ('close', 'Closed')], 'Status from', required=True, copy=False)
    state_to = fields.Selection([
        ('template', 'Template'), ('draft', 'New'), ('open', 'In Progress'),
        ('cancelled', 'Cancelled'), ('pending', 'Pending'),
        ('close', 'Closed')], 'Status to', required=True, copy=False)

    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    project_id = fields.Many2one('project.project', 'Project', required=True)
    value = fields.Float('Value', store=True, compute='_compute_value')


class Project(models.Model):

    _inherit = 'project.project'

    state_history_ids = fields.One2many(
        'project.state.history', 'project_id', string='State history',
        readonly=True)

    @api.multi
    def write(self, values):
        if ('state' in values.keys()):
            state_history_obj = self.env['project.state.history']
            state_to = values['state']
            for project in self:
                state_from = project.state
                state_history_dic = {'state_from': state_from,
                                     'state_to': state_to,
                                     'project_id': project.id
                                     }
                state_history_obj.create(state_history_dic)
            return super(Project, self).write(values)
        else:
            return super(Project, self).write(values)
