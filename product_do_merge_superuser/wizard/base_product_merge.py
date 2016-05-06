# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class MergeProductAutomatic(models.TransientModel):

    _inherit = 'base.product.merge.automatic.wizard'

    @api.multi
    def start_process_cb(self):
        self.sudo().super(MergeProductAutomatic, self).start_process_cb()

    @api.multi
    def next_cb(self):
        self.sudo().super(MergeProductAutomatic, self).next_vb()

    @api.multi
    def merge_cb(self):
        self.sudo().super(MergeProductAutomatic, self).merge_cb()
