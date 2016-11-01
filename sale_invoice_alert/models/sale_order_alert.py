# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class SaleOrderAlert(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for sale_order in self:
            if sale_order.partner_id:
                today = fields.datetime.now()
                invoices = self.env['account.invoice'].search(
                    [('partner_id', '=', sale_order.partner_id.id),
                     ('date_due', '<', today),
                     ('type', '=', 'out_invoice'),
                     ('state', '=', 'open')])
                if invoices:
                    raise Warning(_('The customer has pending invoices.'))
        return super(SaleOrderAlert, self).action_button_confirm()
