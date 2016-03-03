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

_TASK_STATE = [('draft', 'New'), ('open', 'In Progress'),
               ('pending', 'Pending'), ('ready', 'Ready'),
               ('done', 'Done'), ('cancelled', 'Cancelled')]


class project_task_type(models.Model):

    _inherit = 'project.task.type'
    state = fields.Selection(_TASK_STATE, 'Related Status', required=True,
                             default='open')

    @api.multi
    def mark_done(self):
        values = {
            'state': 'done',
            'name': _('Done'),
            'readonly': 'True',
        }
        self.write(values)
        return True

    _defaults = {
        'fold': False,
        'case_default': False
    }


class task(models.Model):

    _inherit = 'project.task'

    @api.one
    @api.depends('stage_id')
    def _compute_state(self):
        if self.stage_id:
            self.state = self.stage_id.state
        else:
            self.state = 'draft'

    state = fields.Selection(
        _TASK_STATE, string="Status", readonly=True, store=True,
        compute='_compute_state')
