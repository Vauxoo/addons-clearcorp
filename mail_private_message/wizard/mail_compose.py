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
        return super(Compose, self).send_mail()

    @api.model
    def get_mail_values(self, wizard, res_ids):
        res = super(Compose, self).get_mail_values(wizard, res_ids)
        for res_id in res.keys():
            res[res_id].update({'privacity': wizard.privacity})
        return res
