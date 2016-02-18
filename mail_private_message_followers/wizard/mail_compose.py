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
