from openerp import models, fields, api, _
from openerp.exceptions import Warning


class origin_task(models.Model):

    _name = 'project.origin.task'

    origin_task_id = fields.Many2one('project.task', string="Name")
    reassignment_hour = fields.Float('Reassignment Hour')
    reassignment_hour_id = fields.Many2one('project.reassignment.hours')
    project_origin_task = fields.Many2one('project.project', string='Project',
                                          related='origin_task_id.project_id',
                                          readonly=True)
    user_origin_task = fields.Many2one('res.users', string='User',
                                       related='origin_task_id.user_id',
                                       readonly=True)
    ph_origin_task = fields.Float('Planned hours',
                                  related='origin_task_id.planned_hours',
                                  readonly=True)
    rh_origin_task = fields.Float('Remaining hours',
                                  related='origin_task_id.remaining_hours',
                                  readonly=True)

    @api.onchange('origin_task_id')
    def onchange_origin_task_id(self):
        if self.reassignment_hour == 0:
            self.rh_origin_task = self.origin_task_id.remaining_hours


class ReassignmentHours(models.Model):

    _inherit = 'mail.thread'
    _name = 'project.reassignment.hours'

    target_task = fields.Many2one('project.task', string="Target Task")
    origin_task_ids = fields.One2many('project.origin.task',
                                      'reassignment_hour_id',
                                      string="Origin Task")
    project_id = fields.Integer('Project')
    type_task_id = fields.Integer('Task type')
    total_time_reassignment = fields.Float(
        'Total Time Reassignment',
        compute='_compute_total_time_reassignment',
        inverse='_inverse_total_time_reassignment')
    inv_total_time_reassignment = fields.Float('Set Total Time Reassignment',
                                               default=0)
    date = fields.Date('Date', required=True)
    reason = fields.Many2one('project.reassignment.reason', string='Reason',
                             required=True)
    detail = fields.Text('Detail', size=200, required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('reassignment', 'Reassignment')],
                             string='State', default='draft')

    @api.onchange('target_task')
    def onchange_target_task(self):
        self.project_id = self.target_task.project_id
        self.type_task_id = self.target_task.work_type_id

    @api.onchange('origin_task_ids')
    def onchange_origin_task(self):
        self.inv_total_time_reassignment = 0

    @api.depends('origin_task_ids')
    def _compute_total_time_reassignment(self):
        for reassignment in self:
            if reassignment.inv_total_time_reassignment:
                reassignment.total_time_reassignment = \
                    reassignment.inv_total_time_reassignment
            else:
                for task in reassignment.origin_task_ids:
                    reassignment.total_time_reassignment = \
                        reassignment.total_time_reassignment +\
                        task.reassignment_hour
        return True

    def _inverse_total_time_reassignment(self):
        for reassignment in self:
            reassignment.inv_total_time_reassignment =\
                reassignment.total_time_reassignment
        return True

    @api.multi
    def set_approve(self):
        for reassignment in self:
            reassignment.state = 'approve'
        return True

    @api.multi
    def reassignment_hours(self):
        for reassignment in self:
            if not reassignment.target_task:
                for task in reassignment.origin_task_ids:
                    if task.reassignment_hour <= \
                            task.origin_task_id.remaining_hours:
                        task.origin_task_id.reassignment_hour =\
                            task.reassignment_hour * -1
                    else:
                        raise Warning('Remaining hours should be more than '
                                      'Reassignment hours')
            if not reassignment.origin_task_ids:
                if not reassignment.target_task.reassignment_hour:
                    reassignment.target_task.write(
                        {'reassignment_hour': self.total_time_reassignment})
                else:
                    reassignment.target_task.write(
                        {'reassignment_hour':
                         reassignment.target_task.reassignment_hour +
                         self.total_time_reassignment})
            else:
                for task in reassignment.origin_task_ids:
                    if task.reassignment_hour <= \
                            task.origin_task_id.remaining_hours:
                        task.origin_task_id.reassignment_hour = \
                            task.reassignment_hour * -1
                    else:
                        raise Warning('Remaining hours should be more than'
                                      'Reassignment hours')
                reassignment.target_task.write({'reassignment_hour':
                                                self.total_time_reassignment})
        reassignment.state = 'reassignment'
        return True


class projectTask(models.Model):

    _inherit = 'project.task'

    reassignment_hour = fields.Float('Reassignment Hour', readonly=True)


class reassignmentReason(models.Model):

    _name = 'project.reassignment.reason'

    name = fields.Char('Reassignment Reason', size=50, required=True)
    active = fields.Boolean('Active')
