# -*- coding: utf-8 -*-
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).

from odoo import models, fields, api


class PurchaseRequisition(models.Model):

    _inherit = 'purchase.requisition'

    group_id = fields.Many2one('procurement.group', 'Procurement group')
    sale_id = fields.Many2one('sale.order', 'Sale order', related='group_id.sale_id')


class ProcurementRule(models.Model):

    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        if product_id.purchase_requisition != 'tenders' or 'group_id' not in values:
            return super(ProcurementRule, self).\
                _run_buy(product_id, product_qty, product_uom, location_id, name, origin, values)
        requisition = self.env['purchase.requisition'].search([
            ('group_id', '=', values['group_id'].id),
            ('company_id', '=', values['company_id'].id),
            ('state', '=', 'draft')], limit=1)
        req_values = self.env['purchase.requisition']._prepare_tender_values(product_id, product_qty, product_uom,
                                                                             location_id, name, origin, values)
        if not requisition:
            req_values['picking_type_id'] = self.picking_type_id.id
            req_values['group_id'] = values['group_id'].id
            req_values['name'] = values['group_id'].name
            self.env['purchase.requisition'].create(req_values)
        else:
            requisition.line_ids = req_values['line_ids']
        return True
