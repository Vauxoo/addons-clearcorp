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

from openerp import models, api
from openerp.exceptions import AccessDenied


class Users(models.Model):

    _inherit = 'res.users'

    @api.model
    def pos_verify_discount(self, login, password):
        # Look for the user with login = user
        user = self.search([('login','=', login)], limit=1)
        if user:
            # Check the user credentials
            try:
                user.check_credentials(password)
                if user.has_group('pos_discount_confirm.group_pos_discount'):
                    return 'go'
                return 'no-group'
            except AccessDenied:
                return 'error'
        return 'error'