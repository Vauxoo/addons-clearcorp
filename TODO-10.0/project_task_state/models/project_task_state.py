# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _

_TASK_STATE = [('draft', 'New'), ('open', 'In Progress'),
               ('pending', 'Pending'), ('ready', 'Ready'),
               ('done', 'Done'), ('cancelled', 'Cancelled')]


class ProjectTaskType(models.Model):
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


class Task(models.Model):
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
