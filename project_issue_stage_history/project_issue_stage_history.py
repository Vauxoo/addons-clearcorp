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
from openerp.fields import Many2one
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProjectIssueStageHistory(models.Model):

    _name = 'project.issue.stage.history'

    @api.one
    @api.depends('date', 'issue_id')
    def _compute_value(self):
        last_history = self.search([
            ('issue_id', '=', self.issue_id.id),
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

    stage_from_id = Many2one('project.task.type', 'Stage from',
                             select=True, copy=False)
    stage_to_id = Many2one('project.task.type', 'Stage to',
                           select=True, copy=False)
    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    issue_id = fields.Many2one('project.issue', 'Issue', required=True, ondelete='cascade')
    value = fields.Float('Value', store=True, compute='_compute_value')


class ProjectIssue(models.Model):

    _inherit = 'project.issue'

    issue_stage_history_ids = fields.One2many(
        'project.issue.stage.history', 'issue_id', string='Stage History',
        readonly=True)

    @api.multi
    def write(self, values):
        if ('stage_id' in values.keys()):
            stage_history_obj = self.env['project.issue.stage.history']
            stage_to_id = values['stage_id']
            for issue in self:
                stage_from_id = issue.stage_id.id
                stage_history_dic = {'stage_from_id': stage_from_id,
                                     'stage_to_id': stage_to_id,
                                     'issue_id': issue.id
                                     }
                stage_history_obj.create(stage_history_dic)
            return super(ProjectIssue, self).write(values)
        else:
            return super(ProjectIssue, self).write(values)
