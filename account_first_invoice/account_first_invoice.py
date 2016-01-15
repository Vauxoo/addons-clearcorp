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


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    first_invoicing = fields.Boolean(string='Is first invoice',
                                  compute='_compute_is_first_invoice')

    @api.one
    @api.depends('partner_id', 'date_invoice')
    def _compute_is_first_invoice(self):
        other_invoice = self.env['account.invoice'].search_count(
            [('partner_id','=',self.partner_id.id),
             ('date_invoice','<',self.date_invoice)])
        if other_invoice:
            self.first_invoicing = False
        else:
            self.first_invoicing = True