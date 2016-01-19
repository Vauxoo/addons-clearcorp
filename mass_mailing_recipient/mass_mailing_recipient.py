# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class MassMailing(models.Model):

    _inherit = 'mail.mail.statistics'

    recipient_ids = fields.Many2many(
        'res.partner', string='To (Partners)')
    email_to = fields.Text('To', readonly=True)

    def create(self, cr, uid, values, context=None):
        mail_mail_obj = self.pool.get('mail.mail')
        if 'mail_mail_id' in values:
            mail_mail_id = values['mail_mail_id']
            mail_mail = mail_mail_obj.browse(cr, uid, mail_mail_id,
                                             context=context)
            values['email_to'] = mail_mail.email_to
            values['recipient_ids'] = [(4, recipient.id) for recipient in
                                       mail_mail.recipient_ids]
        res = super(MassMailing, self).create(cr, uid, values, context=context)
        return res
