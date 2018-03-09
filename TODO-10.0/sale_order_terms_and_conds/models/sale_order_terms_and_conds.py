# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrderTermsAndConditions(models.Model):

    _name = 'sale.order.termsandconditions'
    _description = __doc__

    name = fields.Char(string='Name')
    html_template = fields.Html(string='Template html')


class SaleOrder(models.Model):

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
