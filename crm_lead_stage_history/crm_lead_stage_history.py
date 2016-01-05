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


class CRMLeadStageHistory(models.Model):
    _name = 'crm.lead.stage.history'

    @api.one
    @api.depends('date', 'lead_id')
    def _compute_value(self):
        last_history = self.search([
            ('lead_id', '=', self.lead_id.id),
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

    stage_from_id = Many2one('crm.case.stage', 'Stage from',
                             select=True, copy=False)
    stage_to_id = Many2one('crm.case.stage', 'Stage to',
                           select=True, copy=False)
    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    lead_id = fields.Many2one('crm.lead', 'Lead', required=True)
    value = fields.Float('Value', store=True, compute='_compute_value')


class CRMLead(models.Model):

    _inherit = 'crm.lead'

    lead_stage_history_ids = fields.One2many(
        'crm.lead.stage.history', 'lead_id', string='Stage History',
        readonly=True)

    @api.multi
    def write(self, values):
        if ('stage_id' in values.keys()):
            stage_history_obj = self.env['crm.lead.stage.history']
            stage_to_id = values['stage_id']
            for lead in self:
                stage_from_id = lead.stage_id.id
                stage_history_dic = {'stage_from_id': stage_from_id,
                                     'stage_to_id': stage_to_id,
                                     'lead_id': lead.id
                                     }
                stage_history_obj.create(stage_history_dic)
            return super(CRMLead, self).write(values)
        else:
            return super(CRMLead, self).write(values)
