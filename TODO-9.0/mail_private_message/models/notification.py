# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

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
        return super(Notification, self)._notify(
            message_id, partners_to_notify=partners_to_notify,
            force_send=force_send, user_signature=user_signature)
