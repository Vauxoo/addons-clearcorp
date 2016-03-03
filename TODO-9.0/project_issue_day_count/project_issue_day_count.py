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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class ProjectIssue(models.Model):

    _inherit = 'project.issue'

    @api.one
    @api.depends('date_deadline')
    def _compute_day_count(self):
        if self.date_deadline:
            today = fields.date.today()
            deadline = datetime.strptime(self.date_deadline,
                                         DEFAULT_SERVER_DATE_FORMAT).date()
            self.day_count = (deadline - today).days

    day_count = fields.Integer('Quantity of days',
                               compute='_compute_day_count')
