# -*- coding: utf-8 -*-
# © <YEAR(S)> ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class Accountinvoice(models.Model):
    _inherit = "account.invoice"

    incoterm = fields.Many2one('stock.incoterms', string='Incoterm')


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    incoterm = fields.Many2one('stock.incoterms', string='Incoterm')


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _prepare_procurement_group(self, order):
        res = super(SaleOrder, self)._prepare_procurement_group(order)
        res.update({'incoterm': order.incoterm and order.incoterm.id or False})
        return res

    @api.multi
    def manual_invoice(self):
        res = super(SaleOrder, self).manual_invoice()
        for order in self:
            for invoice in order.invoice_ids:
                if invoice.state == 'draft':
                    invoice.incoterm = order.incoterm
        return res


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        # note: we cannot rely on the procurement_group argument which can be
        # empty, in which case the super() implementation will create a new
        # group -> we use the procurement.group of the picking.
        _super = super(StockMove, self)
        res = _super._picking_assign(procurement_group,
                                     location_from,
                                     location_to)
        for picking in self.mapped('picking_id'):
            group = picking.group_id
            if not group:
                continue
            changes = {}
            changes['incoterm'] = group.incoterm.id
            picking.write(changes)
        return res


class Picking(models.Model):

    _inherit = "stock.picking"

    incoterm = fields.Many2one('stock.incoterms', string='Incoterm')

    @api.cr_uid_ids
    def action_invoice_create(self, cr, uid, ids, journal_id, group=False,
                              type='out_invoice', context=None):
        picking = self.browse(cr, uid, ids[0], context=context)
        ctx = context.copy()
        ctx.update({
            'incoterm': picking.incoterm.id or False
        })
        return super(Picking, self).action_invoice_create(
            cr, uid, ids, journal_id, group=group, type=type, context=ctx)

    @api.cr_uid_ids
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id,
                          move, context=None):
        res = super(Picking, self)._get_invoice_vals(
            cr, uid, key, inv_type, journal_id, move, context=context)
        res['incoterm'] = context.get('incoterm', False)
        return res
