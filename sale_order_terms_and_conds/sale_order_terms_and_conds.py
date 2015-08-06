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


class sale_order_termsandconditions(models.Model):
    """Templates"""

    _name = 'sale.order.termsandconditions'
    _description = __doc__

    name = fields.Char(string='Name')
    html_template = fields.Html(string='Template html')


class sale_order(models.Model):

    _inherit = 'sale.order'

    terms_id = fields.Many2one('sale.order.termsandconditions',
                               string="Template", readonly=True,
                               states={'draft': [('readonly', False)],
                                       'sent': [('readonly', False)]})
    note = fields.Html(readonly=True, states={'draft': [('readonly', False)],
                                              'sent': [('readonly', False)]})

    @api.onchange('terms_id')
    def onchange_html_template(self):
        if self.terms_id:
            self.note = self.terms_id.html_template
