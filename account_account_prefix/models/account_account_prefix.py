# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountAccount(models.Model):

    _inherit = 'account.account'

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        res = super(AccountAccount, self).name_get()
        result = []
        for account in self:
            name = account.company_id.prefix+' '+account.name
            result.append((account.id, name))
        return result
