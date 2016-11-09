# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp import SUPERUSER_ID


class MergePartnerAutomatic(models.TransientModel):

    _inherit = 'base.partner.merge.automatic.wizard'

    def start_process_cb(self, cr, uid, ids, context=None):
        res = super(MergePartnerAutomatic, self).start_process_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res

    def next_cb(self, cr, uid, ids, context=None):
        res = super(MergePartnerAutomatic, self).next_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res

    def merge_cb(self, cr, uid, ids, context=None):
        res = super(MergePartnerAutomatic, self).merge_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res

    def automatic_process_cb(self, cr, uid, ids, context=None):
        res = super(MergePartnerAutomatic, self).automatic_process_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res(self, cr, uid, ids, context=None)

    def update_all_process_cb(self, cr, uid, ids, context=None):
        res = super(MergePartnerAutomatic, self).update_all_process_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res
