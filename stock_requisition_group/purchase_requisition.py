# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, fields, api


class PurchaseRequisition(models.Model):

    _inherit = 'purchase.requisition'

"""
    @api.model
    def _prepare_purchase_order_line(
            self, requisition, requisition_line, purchase_id, supplier):
        res = super(PurchaseRequisition, self)._prepare_purchase_order_line(
            requisition, requisition_line, purchase_id, supplier)
        if requisition_line.procurement_id:
            res.update({
                'procurement_ids': [(4, requisition_line.procurement_id.id)]
            })
        return res
"""

    group_id = fields.Many2one('procurement.group', string='Procurement Group')
    name = fields.Char(default='')


class PurchaseRequisitionLine(models.Model):

    _inherit = 'purchase.requisition.line'

    procurement_id = fields.Many2one(
        'procurement.order', string='Procurement Order')
