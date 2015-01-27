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
from openerp.exceptions import Warning

class ResourceReservation(models.Model):
    """Resource Reservation"""

    _name= 'project.event.resource.reservation'
    _inherit = 'mail.thread'
    _description = __doc__

    _track = {
        'state': {
            'project_event.mt_reservation_draft': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'draft',
            'project_event.mt_reservation_valid': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'valid',
            'project_event.mt_reservation_cancel': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'cancel',
        },
    }

    @api.one
    def is_valid(self):
        if not self.resource_id.unlimited:
            #event_obj = self.env['calendar.event']
            if self.allday:
                result = self.search_count([('allday','=',True),
                    ('resource_id','=',self.resource_id.id),('state','=','valid'),
                    '|','&',('start_date','>=',self.start_date),('start_date','<=',self.stop_date),
                    '|','&',('stop_date','>=',self.start_date),('stop_date','<=',self.stop_date),
                    '&',('start_date','<=',self.start_date),('stop_date','>=',self.stop_date),])
                if result:
                    return False
                result = self.search_count([('allday','=',False),
                    ('resource_id','=',self.resource_id.id),('state','=','valid'),
                    '|','&',('start_datetime','>=',self.start_date),('start_datetime','<=',self.stop_date),
                    '|','&',('stop_datetime','>=',self.start_date),('stop_datetime','<=',self.stop_date),
                    '&',('start_datetime','<=',self.start_date),('stop_datetime','>=',self.stop_date)])
                if result:
                    return False
                return True
            else:
                result = self.search_count([('allday','=',True),
                    ('resource_id','=',self.resource_id.id),('state','=','valid'),
                    '|','&',('start_date','>=',self.start_datetime),('start_date','<=',self.stop_datetime),
                    '|','&',('stop_date','>=',self.start_datetime),('stop_date','<=',self.stop_datetime),
                    '&',('start_date','<=',self.start_datetime),('stop_date','>=',self.stop_datetime)])
                if result:
                    return False
                result = self.search_count([('allday','=',False),
                    ('resource_id','=',self.resource_id.id),('state','=','valid'),
                    '|','&',('start_datetime','>=',self.start_datetime),('start_datetime','<=',self.stop_datetime),
                    '|','&',('stop_datetime','>=',self.start_datetime),('stop_datetime','<=',self.stop_datetime),
                    '&',('start_datetime','<=',self.start_datetime),('stop_datetime','>=',self.stop_datetime)])
                if result:
                    return False
                return True
        else:
            return True

    @api.one
    def validate_reservation(self):
        result = self.is_valid()[0]
        if result:
            self.state = 'valid'
        else:
            raise Warning(_('This reservation can not be validated '
                'the resource %s is already in use.') % self.resource_id.display_name)

    @api.one
    def cancel_reservation(self):
        self.state = 'cancel'

    @api.one
    def set_as_draft(self):
        self.state = 'draft'

    @api.multi
    @api.depends('state')
    def _compute_state_id(self):
        for reservation in self:
            state_color = self.env['project.event.reservation.color'].search(
                [('state','=',reservation.state)])
            if state_color:
                reservation.state_id = state_color
            else:
                reservation.state_id = False

    @api.onchange('category_id')
    def onchange_category_id(self):
        if not self.category_id:
            self.resource_id = False
            return {}
        resource_obj = self.env['project.event.resource']
        reservations = []
        if self.event_id.allday:
            result = self.search([('allday','=',True),('state','=','valid'),
                '|','&',('start_date','>=',self.start_date),('start_date','<=',self.stop_date),
                '|','&',('stop_date','>=',self.start_date),('stop_date','<=',self.stop_date),
                '&',('start_date','<=',self.start_date),('stop_date','>=',self.stop_date),])
            if result:
                reservations += result
            result = self.search([('allday','=',False),('state','=','valid'),
                '|','&',('start_datetime','>=',self.start_date),('start_datetime','<=',self.stop_date),
                '|','&',('stop_datetime','>=',self.start_date),('stop_datetime','<=',self.stop_date),
                '&',('start_datetime','<=',self.start_date),('stop_datetime','>=',self.stop_date)])
            if result:
                reservations += result
        else:
            result = self.search([('allday','=',True),('state','=','valid'),
                '|','&',('start_date','>=',self.start_datetime),('start_date','<=',self.stop_datetime),
                '|','&',('stop_date','>=',self.start_datetime),('stop_date','<=',self.stop_datetime),
                '&',('start_date','<=',self.start_datetime),('stop_date','>=',self.stop_datetime)])
            if result:
                reservations += result
            result = self.search([('allday','=',False),('state','=','valid'),
                '|','&',('start_datetime','>=',self.start_datetime),('start_datetime','<=',self.stop_datetime),
                '|','&',('stop_datetime','>=',self.start_datetime),('stop_datetime','<=',self.stop_datetime),
                '&',('start_datetime','<=',self.start_datetime),('stop_datetime','>=',self.stop_datetime)])
            if result:
                reservations += result
        resource_ids = []
        for reserve in reservations:
            resource_ids.append(reserve.resource_id.id)
        resource_ids = list(set(resource_ids))
        return {
            'domain': {
                'resource_id': [('id','not in',resource_ids),('category_id','=',self.category_id.id)]
            }
        }

    event_id = fields.Many2one('project.event.event',
        string='Event', ondelete='cascade')
    category_id = fields.Many2one('project.event.resource.category', string='Resource Category',
        states={'valid': [('readonly', True)], 'cancel': [('readonly', True)]})
    resource_id = fields.Many2one('project.event.resource', string='Resource',
        states={'valid': [('readonly', True)], 'cancel': [('readonly', True)]},
        track_visibility='onchange', required=True)
    state = fields.Selection([('draft','Draft'),('valid','Validated'),
        ('cancel','Cancelled')], string='State', default='draft')
    state_id = fields.Many2one('project.event.reservation.color', string='State Color',
        compute='_compute_state_id', store=True)
    name = fields.Char('Reservation name', related='resource_id.name',
        size=128, readonly=True)
    allday = fields.Boolean('All Day', related='event_id.allday', readonly=True)
    start_date = fields.Date('Start Date', related='event_id.start_date', readonly=True)
    start_datetime = fields.Datetime('Start DateTime', related='event_id.start_datetime', readonly=True)
    stop_date = fields.Date('End Date', related='event_id.stop_date', readonly=True)
    stop_datetime = fields.Datetime('End DateTime', related='event_id.stop_datetime', readonly=True)
    start = fields.Datetime('Calculated start', related='event_id.start', readonly=True)
    stop = fields.Datetime('Calculated stop', related='event_id.stop', readonly=True)
    duration = fields.Float('Duration', related='event_id.duration', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible', related='event_id.user_id', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', related='event_id.project_id', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', related='event_id.task_id', readonly=True)

    _sql_constraints = [('unique_resource_event','UNIQUE(resource_id,event_id)',
        'Resources can only be added once per event.')]