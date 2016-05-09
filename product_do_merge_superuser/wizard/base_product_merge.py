# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv
from openerp import SUPERUSER_ID


class MergeProductAutomatic(osv.TransientModel):

    _inherit = 'base.product.merge.automatic.wizard'

    def start_process_cb(self, cr, uid, ids, context=None):
        res = super(MergeProductAutomatic, self).start_process_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res

    def next_cb(self, cr, uid, ids, context=None):
        res = super(MergeProductAutomatic, self).next_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res

    def merge_cb(self, cr, uid, ids, context=None):
        res = super(MergeProductAutomatic, self).merge_cb(
            cr, SUPERUSER_ID, ids, context=context)
        return res
