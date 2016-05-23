# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class Notification(models.Model):

    _inherit = 'mail.notification'

    @api.model
    def _notify(self, message_id, partners_to_notify=None,
                force_send=False, user_signature=True):
        if 'notify' in self.env.context and not self.env.context['notify']:
            partner_obj = self.env['res.partner']
            message = self.env['mail.message'].browse(message_id)
            partners_to_notify = self.env.context.get('partners_to_notify', [])
            if message.privacity == 'private':
                user_obj = self.pool.get('res.users')
                clean_partners = []
                # clean partners to notify only internal users
                for partner in partner_obj.browse(partners_to_notify):
                    for user in partner.user_ids:
                        if user_obj.has_group(
                                self._cr, user.id, 'base.group_user'):
                            clean_partners.append(partner.id)
                partners_to_notify = clean_partners
        else:
            partners_to_notify = self.env.context.get('partners_to_notify',
                                                      partners_to_notify)
        return super(Notification, self)._notify(
            message_id, partners_to_notify=partners_to_notify,
            force_send=force_send, user_signature=user_signature)
