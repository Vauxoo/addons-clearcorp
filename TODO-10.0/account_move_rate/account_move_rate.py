# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _


class MoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.one
    @api.constrains('currency_id')
    def _get_rate_journal(self):
        for line in self:
            if line.currency_id:
                if line.currency_id.base:
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
        return True


class Move(models.Model):

    _inherit = 'account.move'

    @api.one
    @api.constrains('date')
    def _get_rate_journal(self):
        self.line_ids._get_rate_journal()
