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

from datetime import datetime
from openerp import models, fields, api, _

class PaymentWizard(models.TransientModel):

    _name = 'partner.payment.average.payment.wizard'

    @api.one
    @api.constrains('period_start', 'period_end')
    def _check_seats_limit(self):
        if datetime.strptime(self.period_start.date_start, '%Y-%m-%d') > \
        datetime.strptime(self.period_end.date_start,'%Y-%m-%d'):
            raise Warning(_('Invalid periods selected. Start Period must be previous to '
                            'the End Period.'))

    @api.multi
    def print_report(self):
        # Get all customers if no one is selected
        if not self.partner_ids:
            self.partner_ids = self.env['res.partner'].search([('customer','=',True)])
        data = {
            'form': {
                'start_period_id': self.period_start.id,
                'end_period_id': self.period_end.id,
            }
        }
        res = self.env['report'].get_action(self.partner_ids,
            'partner_payment_average.report_payment_average', data=data)
        return res

    period_start = fields.Many2one('account.period', string='Start Period', required=True)
    period_end = fields.Many2one('account.period', string='End Period', required=True)
    partner_ids = fields.Many2many('res.partner', string='Partners', domain=[('customer','=',True)])