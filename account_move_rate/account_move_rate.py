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


from openerp import models, api, _


class MoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.one
    @api.constrains('currency_id')
    def _get_rate_journal(self):
        for line in self:
            if line.currency_id and line.currency_id.base:
                rate = line.company_id.currency_id.rate_ids.search(
                    [('name', '=', self.move_id.date)])
                if not rate:
                    raise Warning(
                        _('There is no rate available for currency %s')
                        % line.currency_id.name)
            else:
                rate = line.currency_id.rate_ids.search(
                    [('name', '=', self.move_id.date)])
                if not rate:
                    raise Warning(
                        _('There is no rate available for currency %s')
                        % line.currency_id.name)
