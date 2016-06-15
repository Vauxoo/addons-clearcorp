# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class Journal(osv.Model):

    _inherit = 'account.journal'

    _columns = {
        'pay_commission': fields.boolean('Pay Commission'),
    }
