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

import time
from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _

class ResCurrency(models.Model):

    _inherit = 'res.currency'

    sequence = fields.Boolean('Rate Direction', copy=False)

    @api.one
    def get_exchange_rate(self, currency_final, date):
        """
        :param name: date of exchange rate
        """

        res_currency_base = self.search([('base', '=', True)], limit=1)
        if res_currency_base:
            #res_currency_base = self.browse(cr, uid, res_currency_base_id)[0]
            if self.id == res_currency_base.id:
                #exchange_rate_dict = self.pool.get('res.currency')._current_rate(
                #    cr, uid, [res_currency_final.id], name, arg=None, context=copy_context)
                #result = exchange_rate_dict[res_currency_final.id]
                res = currency_final.with_context(date=date)._get_current_rate()
                return res[currency_final.id]

            elif self.id != currency_final.id:
                res = self.with_context(date=date)._get_current_rate()
                initial_rate = res[self.id]
                res = currency_final.with_context(date=date)._get_current_rate()
                final_rate = res[currency_final.id]
                result = initial_rate * final_rate
            else:
                return 1.00
        else:
            raise Warning(_('Please select your base currency Miscellaneous/Currency'))


class CurrencyRate(models.Model):

    _inherit = 'res.currency.rate'

    name = fields.Date('Date', required=True, select=True,
        default=lambda *a: time.strftime('%Y-%m-%d'))