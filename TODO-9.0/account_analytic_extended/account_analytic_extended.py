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

class AnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.one
    def parent_name_get(self):
        if self.parent_id:
            if self.parent_id.parent_id:
                parent_name = self.parent_id.parent_name_get()[0]
                return parent_name + '/' + self.parent_id.code
            else:
                return self.parent_id.code
        else:
            return ''

    @api.one
    def _short_name(self):
        if self.parent_id:
            parent_name = self.parent_name_get()[0]
            self.short_name = parent_name + '/' + self.name
        else:
            self.short_name = self.name

    short_name = fields.Char ('Account Name', compute='_short_name')

    @api.multi
    def name_get(self):
        result = []
        for account in self:
            result.append((account.id, account.short_name ))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()