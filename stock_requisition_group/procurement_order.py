# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, api


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

"""
    @api.multi
    def name_get(self):
        result = []
        for procurement in self:
            result.append((procurement.id, '%s: %s' % (
                procurement.product_id.display_name or '',
                procurement.origin or '')))
        return result

    @api.model
    def _run(self, procurement):
        if procurement.rule_id and procurement.rule_id.action == 'buy' and \
                procurement.product_id.purchase_requisition:
            res = super(ProcurementOrder, self)._run(procurement)
            # Review if there is any created requisition
            requisition_obj = self.env['purchase.requisition']
            requisition = requisition_obj.search(
                [('group_id', '=', procurement.group_id.id),
                 ('state', '=', 'draft'),
                 ('id', '!=', procurement.requisition_id.id),
                 ('company_id', '=', procurement.company_id.id)], limit=1)
            if requisition:
                for line in procurement.requisition_id.line_ids:
                    line.procurement_id = procurement.id
                    line.requisition_id = requisition.id
                procurement.requisition_id.unlink()
                procurement.requisition_id = requisition.id
            else:
                # Assign the procurement group and
                # assign the sequence to the requisition
                procurement.requisition_id.write({
                    'group_id': procurement.group_id.id,
                    'name': procurement.origin,
                })
                for line in procurement.requisition_id.line_ids:
                    line.procurement_id = procurement.id
            return res
        else:
            return super(ProcurementOrder, self)._run(procurement)
"""
