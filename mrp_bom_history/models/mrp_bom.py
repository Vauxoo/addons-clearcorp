# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    @api.multi
    def _compute_history_item_count(self):
        for bom in self:
            bom.history_item_count = self.env['mrp.bom.history'].search_count(
                [('bom_id', '=', bom.id)]
            )

    history_item_count = fields.Integer(
        'History Items Count', compute='_compute_history_item_count')

    @api.model
    def create(self, vals):
        res = super(MrpBom, self).create(vals)
        vals.update({'bom_id': res.id})
        self.env['mrp.bom.history'].create(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super(MrpBom, self).write(vals)
        for bom in self:
            vals.update({
                'bom_id': bom.id,
                'bom_line_ids': False,
            })
            history_obj = self.env['mrp.bom.history']
            latest_history = history_obj.search(
                [('bom_id', '=', bom.id)], limit=1, order='id desc')
            if latest_history:
                new_history = latest_history.copy()
                new_history.write(vals)
            else:
                new_history_vals = bom.copy_data(default=vals)[0]
                new_history = history_obj.create(new_history_vals)
            history_line_obj = self.env['mrp.bom.line.history']
            for line in bom.bom_line_ids:
                history_line_vals = line.copy_data(default={
                    'bom_id': new_history.id,
                })[0]
                history_line_obj.create(history_line_vals)
        return res
