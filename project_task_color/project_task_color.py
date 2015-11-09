from openerp.osv import osv, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime

class task(osv.Model):
    _inherit = 'project.task'

    def _get_color_code(self, date_start, date_deadline, planned_hours, stage_id):
        """Calculate the current color code for the task depending on the state
        Colors:
        0 -> White          5 -> Aqua
        1 -> Dark Gray      6 -> Light Aqua
        2 -> Red            7 -> Blue
        3 -> Orange         8 -> Purple
        4 -> Green          9 -> Pink
        @param self: The object pointer.
        @param date_start: The string initial date
        @param date_deadline: The string dateline
        @param planned_hours: Total planned hours for the task
        @param state: The current task state
        @return: An integer that represents the current task state as a color
        """
        if stage_id:
            # Done task COLOR: GRAY
            return '1'
        else:
            if date_deadline:
                if date_start:
                    if planned_hours:
                        date_start = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
                        date_deadline = datetime.strptime(date_deadline, '%Y-%m-%d')
                        total_time_delta = relativedelta(date_deadline, date_start)
                        left_hours_delta = relativedelta(date_deadline, datetime.today())
                        total_time = (total_time_delta.days * 24) + total_time_delta.hours + (total_time_delta.minutes / 60)
                        left_hours = (left_hours_delta.days * 24) + left_hours_delta.hours + (left_hours_delta.minutes / 60)
                        percentage_left = float(left_hours) / float(total_time)
                        if percentage_left >= 0.70:
                            # COLOR: BLUE
                            return '7'
                        elif percentage_left >= 0.50:
                            # COLOR: GREEN
                            return '4'
                        elif percentage_left >= 0.30:
                            # COLOR: ORANGE
                            return '3'
                        else:
                            # COLOR: RED
                            return '2'
                        # COLOR: PINK
                        return '9'
                    else:
                        # Not planned hours available COLOR: PURPLE
                        return '8'
                else:
                    # No date_start COLOR: AQUA
                    return '6'
            else:
                # No deadline available COLOR: WHITE
                return '0'

    def _compute_color(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = self._get_color_code(task.date_start, task.date_deadline, task.planned_hours, task.stage_id)
        return res
    
    _columns = {
        'color': fields.function(_compute_color, type='integer', string='Color Index'),
        }