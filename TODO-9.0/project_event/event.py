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

import pytz
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Event(models.Model):
    """Events"""

    _name= 'project.event.event'
    _inherit = 'mail.thread'
    _description = __doc__

    _track = {
        'state': {
            'project_event.mt_event_draft': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'draft',
            'project_event.mt_event_valid': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'valid',
            'project_event.mt_event_cancel': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'cancel',
        },
    }

    @api.onchange('allday')
    def onchange_allday(self):
        if self.allday:
            if self.start_datetime:
                self.start_date = self.start_datetime[0:10]
            if self.stop_datetime:
                self.stop_date = self.stop_datetime[0:10]
            self.start_datetime = False
            self.stop_datetime = False
        else:
            # Check if timezones are available to display the correct date
            if self.env.context.get('tz'):
                tz = self.env.context.get('tz')
                local_timezone = pytz.timezone (tz)
                if self.start_date:
                    start_date = datetime.strptime (self.start_date, DEFAULT_SERVER_DATE_FORMAT)
                    local_dt = local_timezone.localize(start_date, is_dst=False)
                    utc_dt = local_dt.astimezone (pytz.utc)
                    self.start_datetime = datetime.strftime(utc_dt, DEFAULT_SERVER_DATETIME_FORMAT)
                if self.stop_date:
                    stop_date = datetime.strptime (self.stop_date, DEFAULT_SERVER_DATE_FORMAT)
                    local_dt = local_timezone.localize(stop_date, is_dst=False)
                    utc_dt = local_dt.astimezone (pytz.utc)
                    self.stop_datetime = datetime.strftime(utc_dt, DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                if self.start_date:
                    self.start_datetime = self.start_date + ' 00:00:00'
                if self.stop_date:
                    self.stop_datetime = self.stop_date + ' 00:00:00'
            self.start_date = False
            self.stop_date = False

    @api.onchange('task_id')
    def onchange_project_id(self):
        if self.task_id:
            self.project_id = self.task_id.project_id
        

    @api.constrains('start_date','stop_date')
    def _constraint_dates(self):
        if self.start_date and self.stop_date:
            if self.start_date > self.stop_date:
                raise ValidationError(_('Start date must occurr before End Date.'))
        return True

    @api.constrains('start_datetime','stop_datetime')
    def _constraint_datetimes(self):
        if self.start_datetime and self.stop_datetime:
            if self.start_datetime > self.stop_datetime:
                raise ValidationError(_('Start date must occurr before End Date.'))
        return True

    @api.multi
    @api.depends('start_date','stop_date',
        'start_datetime','stop_datetime','allday')
    def _compute_dates(self):
        for rec in self:
            if rec.allday:
                if rec.env.context.get('tz'):
                    tz = rec.env.context.get('tz')
                    local_timezone = pytz.timezone (tz)
                    start_date = datetime.strptime (rec.start_date, DEFAULT_SERVER_DATE_FORMAT)
                    local_dt = local_timezone.localize(start_date, is_dst=False)
                    utc_dt = local_dt.astimezone (pytz.utc)
                    rec.start = datetime.strftime(utc_dt, DEFAULT_SERVER_DATETIME_FORMAT)
                    stop_date = datetime.strptime (rec.stop_date, DEFAULT_SERVER_DATE_FORMAT)
                    local_dt = local_timezone.localize(stop_date, is_dst=False)
                    utc_dt = local_dt.astimezone (pytz.utc)
                    rec.stop = datetime.strftime(utc_dt, DEFAULT_SERVER_DATETIME_FORMAT)
                else:
                    rec.start = rec.start_date
                    rec.stop = rec.stop_date
            else:
                rec.start = rec.start_datetime
                rec.stop = rec.stop_datetime

    """@api.multi
    def _inverse_dates(self):
        for event in self:
            start_date = event.start
            end_date = event.stop
            if event.allday:
                event.start_date = start_date[0:10]
                event.stop_date = end_date[0:10]
                event.start_datetime = False
                event.stop_datetime = False
            else:

                event.start_datetime = start_date
                event.stop_datetime = end_date
                event.start_date = False
                event.stop_date = False"""

    @api.multi
    @api.depends('start','stop')
    def _compute_duration(self):
        for rec in self:
            if rec.start and rec.stop:
                start_date = datetime.strptime(rec.start, DEFAULT_SERVER_DATETIME_FORMAT)
                stop_date = datetime.strptime(rec.stop, DEFAULT_SERVER_DATETIME_FORMAT)
                duration = stop_date - start_date
                rec.duration = (float(duration.days) * 24) + (float(duration.seconds) / 3600)
            else:
                rec.duration = 0.0

    @api.one
    def validate_event(self):
        self.validate_reservations()
        self.state = 'valid'

    @api.one
    def cancel_event(self):
        for reservation in self.reservation_ids:
            if reservation.state != 'cancel':
                reservation.cancel_reservation()
        self.state = 'cancel'

    @api.one
    def set_as_draft(self):
        for reservation in self.reservation_ids:
            reservation.set_as_draft()
        self.state = 'draft'

    @api.one
    def validate_reservations(self):
        for reservation in self.reservation_ids:
            reservation.validate_reservation()

    name = fields.Char('Event', size=128, required=False,
        states={'valid': [('readonly', True)], 'cancel': [('readonly', True)]})
    allday = fields.Boolean('All Day', default=True, states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    start_date = fields.Date('Start Date', default=lambda slf: datetime.strftime(
        datetime.today(), DEFAULT_SERVER_DATE_FORMAT), states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    start_datetime = fields.Datetime('Start DateTime', states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    stop_date = fields.Date('End Date', default=lambda slf: datetime.strftime(
        datetime.today(), DEFAULT_SERVER_DATE_FORMAT), states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    stop_datetime = fields.Datetime('End DateTime', states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    start = fields.Datetime('Calculated start', compute='_compute_dates', store=True)
    stop = fields.Datetime('Calculated stop', compute='_compute_dates', store=True)
    duration = fields.Float('Duration', compute='_compute_duration')
    user_id = fields.Many2one('res.users', string='Responsible',
        default=lambda slf: slf.env.user, required=True, states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    project_id = fields.Many2one('project.project', string='Project', required=True,
        states={'valid': [('readonly', True)], 'cancel': [('readonly', True)]})
    task_id = fields.Many2one('project.task', string='Task', states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    reservation_ids = fields.One2many('project.event.resource.reservation', 'event_id',
        string='Resources', states={'valid': [('readonly', True)], 'cancel': [('readonly', True)]})
    description = fields.Text('Description', states={'valid': [('readonly', True)],
        'cancel': [('readonly', True)]})
    attendee_ids = fields.Many2many('res.partner', string='Attendeees',
        states={'valid': [('readonly', True)], 'cancel': [('readonly', True)]})
    state = fields.Selection([('draft','Draft'),('valid','Validated'),
        ('cancel','Cancelled')], string='State', default='draft')

    @api.multi
    def write(self, values):
        keys = values.keys()
        if 'start_date' in keys or 'start_datetime' in keys or \
            'stop_date' in keys or 'stop_datetime' in keys:
            res = super(Event, self).write(values)
            for event in self:
                for reservation in self.reservation_ids:
                    if reservation.state != 'cancel':
                        reservation.set_as_draft()
            return res
        else:
            return super(Event, self).write(values)
