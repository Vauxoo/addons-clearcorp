from openerp import models, fields, api


class task(models.Model):
    _inherit = 'project.task'

    @api.one
    @api.depends('state',
                 'date_deadline',
                 'planned_hours',
                 'progress')
    def _get_color_code(self):
        """Calculate the current color code for the task depending on the state
        Colors:
        0 -> White          5 -> Aqua
        1 -> Dark Gray      6 -> Light Aqua
        2 -> Red            7 -> Blue
        3 -> Orange         8 -> Purple
        4 -> Green          9 -> Pink
        @param self: The object pointer.
        @param date_deadline: The string dateline
        @param planned_hours: Total planned hours for the task
        @param state: The current task state
        @param progress: The current task progress
        @return: An integer that represents the current task state as a color
        """
        if self.state == 'done':
            # Done task COLOR: GRAY
            self.color = 1
        else:
            if self.date_deadline and self.date_deadline < fields.Date.today():
                # COLOR: RED
                self.color = 2
            if self.planned_hours:
                if self.progress >= 70.0:
                    # COLOR: BLUE
                    self.color = 7
                elif self.progress >= 50.0:
                    # COLOR: GREEN
                    self.color = 4
                elif self.progress >= 30.0:
                    # COLOR: ORANGE
                    self.color = 3
                else:
                    # COLOR: RED
                    self.color = 2
            else:
                # Not planned hours available COLOR: PURPLE
                self.color = 8

    color = fields.Integer(compute='_get_color_code', string='Color Index')
