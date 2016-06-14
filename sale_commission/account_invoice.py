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
import openerp.addons.decimal_precision as dp


class Invoice(models.Model):

    _inherit = 'account.invoice'
    _name = 'account.invoice'

    @api.onchange('force_commission')
    def onchange_force_commission(self):
        self.commission_percentage = 0.0
        self.post_expiration_days = 0.0

    force_commission = fields.Boolean(
        'Force Commission', help='Check if you want to '
        'pay a fixed commission percentage for this invoice.')
    commission_percentage = fields.Float(
        'Commission', digits=dp.get_precision('Account'))
    post_expiration_days = fields.Integer(
        'Post-Expiration Days', help='Quantity of days '
        'of tolerance between the invoice due date and the payment date.')
