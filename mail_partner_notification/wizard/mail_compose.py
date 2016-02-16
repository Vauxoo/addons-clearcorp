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

from openerp import models, api, SUPERUSER_ID, fields
from openerp.fields import Many2many


class Compose(models.TransientModel):

    _inherit = 'mail.compose.message'

    privacity = fields.Selection(
        [('public', 'Public'), ('private', 'Private')],
        'Privacity', default='public')

    @api.model
    def _default_partner_followers(self):
        if (not self._context['default_model'] or not
                self._context['default_model']):
            return None
        model = self._context['default_model']
        res_id = self._context['default_res_id']
        fol_obj = self.pool.get('mail.followers')
        fol_ids = fol_obj.search(
            self._cr, SUPERUSER_ID, [('res_model', '=', model),
                                     ('res_id', 'in', [res_id])])
        followers = fol_obj.browse(self._cr, self._uid, fol_ids)
        partner_ids = []
        for fol in followers:
            partner_ids.append(fol.partner_id.id)
        return self.pool.get('res.partner').browse(self._cr, self._uid,
                                                   partner_ids)

    followers_ids = Many2many('res.partner',
                              'mail_compose_followers_res_partner_rel',
                              'wizard_id', 'partner_id', string='Followers',
                              default=_default_partner_followers)

    @api.multi
    def send_mail(self):
        self._validate_partners()
        if not self.notify:
            return super(Compose, self.with_context(
                notify=False,
                partners_to_notify=self.partner_ids._ids)).send_mail()
        else:
            all_partners = self.partner_ids._ids + self.followers_ids._ids
            return super(Compose, self.with_context(
                notify=True,
                partners_to_notify=all_partners)).send_mail()
        return super(Compose, self).send_mail()

    @api.model
    def get_mail_values(self, wizard, res_ids):
        res = super(Compose, self).get_mail_values(wizard, res_ids)
        for res_id in res.iteritems():
            res_id[1].update({'privacity': wizard.privacity})
        return res

    @api.depends('privacity')
    def _validate_partners(self):
        if self.privacity == 'public':
            self.followers_ids = None
            self.followers_ids = self._default_partner_followers()
            print "\n\npublic\n\n"
        else:
            all_partners = self.partner_ids + self.followers_ids
            print "\n\n\n", all_partners, "\n\n\n"
            for partner in all_partners:
                if partner.user_ids:
                    for user in partner.user_ids:
                        if user.has_group('base.group_portal'):
                            self.partner_ids = self.partner_ids - partner
                            self.followers_ids = self.followers_ids - partner
                            all_partners = all_partners - partner
                            pass
            print "\n\n\n", all_partners, "\n\n\n"
