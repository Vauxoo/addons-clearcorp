# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(AccountInvoice, self).invoice_validate(
            cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.partner_id.invoice_warn == 'block':
                raise Warning(invoice.partner_id.invoice_warn_msg)
        return res
