# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class Compose(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.onchange('notify')
    def _load_partners(self):
        if (not self.notify):
            self.partner_ids = self.env['res.partner']
            return
        follower_obj = self.env['mail.followers']
        if ('default_model' in self._context.keys()) and\
           ('default_res_id' in self._context.keys()):
            followers = follower_obj.sudo().search([
                ('res_model', '=', self._context['default_model']),
                ('res_id', '=', self._context['default_res_id'])])
            partners = set([])
            partners |= set(
                fo.partner_id.id for fo in followers)
            self.partner_ids = self.env['res.partner'].browse(list(partners))
