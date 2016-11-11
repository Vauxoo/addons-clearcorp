# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for account in self:
            name = ''
            if account.company_id.prefix:
                name += '[' + account.company_id.prefix + ']' + \
                        ' ' + account.code + ' ' + account.name
            else:
                name += account.code + ' ' + account.name
            result.append((account.id, name))
        return result
