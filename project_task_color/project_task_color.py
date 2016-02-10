from openerp import models, fields, api
from datetime import datetime
import openerp.tools as tools


class task(models.Model):
    _inherit = 'project.task'

    @api.one
    @api.depends('state',
                 'date_deadline',
                 'date_start')
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

        deadline = datetime.strptime(self.date_deadline,
                                     tools.DEFAULT_SERVER_DATE_FORMAT)
        date_start = datetime.strptime(self.date_start,
                                       tools.DEFAULT_SERVER_DATETIME_FORMAT)
        today = datetime.now()
        time_diff = deadline - date_start
        if time_diff.seconds:
            total_days = time_diff.days + 1
        else:
            total_days = time_diff.days
        time_diff = deadline - today
        if time_diff.seconds:
            total_disp = time_diff.days + 1
        else:
            total_disp = time_diff.days
        try:
            total_time = float(total_disp) / float(total_days)
        except ZeroDivisionError:
            total_time = 0.0
        if self.state == 'done':
            # Done task COLOR: GRAY
            self.color = 1
        elif self.state == 'cancel':
            self.color = 8
        else:
            if total_time <= 0.2:
                # COLOR: RED
                self.color = 2
            elif total_time > 0.2 and total_time <= 0.4:
                # COLOR: ORANGE
                self.color = 3
            elif total_time > 0.4 and total_time <= 0.6:
                # COLOR: BLUE
                self.color = 7
            elif total_time > 0.6 and total_time <= 0.8:
                # COLOR: AQUA
                self.color = 5
            elif total_time > 0.8 and total_time <= 1.0:
                # COLOR: GREEN
                self.color = 4
            else:
                # COLOR: WHITE
                self.color = 0

    color = fields.Integer(compute='_get_color_code', string='Color Index',
                           store=True)
