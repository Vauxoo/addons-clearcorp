# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class Compose(models.TransientModel):

    _inherit = 'mail.compose.message'

    privacity = fields.Selection(
        [('public', 'Public'), ('private', 'Private')],
        'Privacity', default='public')
    notify = fields.Boolean(default=True)

    @api.multi
    def send_mail(self):
        if not self.notify:
            return super(Compose, self.with_context(
                notify=False,
                partners_to_notify=self.partner_ids._ids)).send_mail()
        return super(Compose, self.with_context(
            notify=True,
            partners_to_notify=self.partner_ids._ids)).send_mail()

    @api.model
    def get_mail_values(self, wizard, res_ids):
        res = super(Compose, self).get_mail_values(wizard, res_ids)
        for res_id in res.keys():
            res[res_id].update({'privacity': wizard.privacity})
        return res
