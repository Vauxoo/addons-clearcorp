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

from openerp import fields, models, api, _


class delivery_carrier(models.Model):

    _inherit = 'delivery.carrier'

    split_invoice = fields.Boolean('Split Invoice')


class account_invoice_line(models.Model):

    _inherit = 'account.invoice.line'

    delivery_line = fields.Boolean('Delivery line', default=False)


class stock_picking(models.Model):

    _inherit = 'stock.picking'

    carrier_invoice_control = fields.Selection(
        [("invoiced", "Invoiced"), ("2binvoiced", "To Be Invoiced"),
         ("none", "Not Applicable")], "Carrier Invoice Control",)

    @api.multi
    @api.onchange('partner_id')
    def partner_id_change(self):
        self.carrier_id = self.partner_id.property_delivery_carrier or False

    def _invoice_create_line(
            self, cr, uid, moves, journal_id,
            inv_type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_ids = super(stock_picking, self)._invoice_create_line(
            cr, uid, moves, journal_id, inv_type=inv_type, context=context)
        delivey_invoices = {}
        for move in moves:
            key = (move.picking_id.partner_id.id, move.picking_id.id)
            for invoice in move.purchase_line_id.order_id.invoice_ids:
                if invoice.id in invoice_ids:
                    if key not in delivey_invoices:
                        delivey_invoices[key] = invoice
        if delivey_invoices:
            for key, invoice in delivey_invoices.items():
                picking = self.browse(cr, uid, key[1], context=context)
                if picking.carrier_id.split_invoice or \
                        picking.carrier_invoice_control == 'none':
                    if picking.invoice_state == 'invoiced' and \
                            picking.carrier_invoice_control == '2binvoiced' \
                            and 'invoice_delivery' not in context:
                        invoice_line = invoice_line_obj.search(
                            cr, uid, [('invoice_id', '=', invoice.id),
                                      ('delivery_line', '=', True)],
                            context=context)
                        if invoice_line:
                            invoice_line_obj.unlink(cr, uid, invoice_line)
                            invoice_obj.button_compute(
                                cr, uid, [invoice.id], context=context,
                                set_total=(inv_type in ('out_invoice',
                                                        'out_refund')))
                    if picking.invoice_state == 'invoiced' and \
                            picking.carrier_invoice_control == '2binvoiced' \
                            and 'invoice_delivery' in context:
                        invoice_line = invoice_line_obj.search(
                            cr, uid, [('invoice_id', '=', invoice.id),
                                      ('delivery_line', '=', False)],
                            context=context)
                        invoice.write({
                            'partner_id': picking.carrier_id.partner_id.id
                        })
                        if invoice_line:
                            invoice_line_obj.unlink(cr, uid, invoice_line)
                            invoice_obj.button_compute(
                                cr, uid, [invoice.id], context=context,
                                set_total=(inv_type in ('out_invoice',
                                                        'out_refund')))
                        picking.carrier_invoice_control = 'invoiced'
                else:
                    picking.carrier_invoice_control = picking.invoice_state
        if not delivey_invoices and 'invoice_delivery' in context:
            for move in moves:
                key = (move.picking_id.partner_id.id, move.picking_id.id)
                for invoice_id in invoice_ids:
                    invoice = self.pool.get('account.invoice').browse(
                        cr, uid, invoice_id, context=context)
                    if invoice.origin == move.picking_id.name:
                        if key not in delivey_invoices:
                            delivey_invoices[key] = invoice

            for key, invoice in delivey_invoices.items():
                picking = self.browse(cr, uid, key[1], context=context)
                if picking.invoice_state == 'invoiced' and \
                        picking.carrier_invoice_control == '2binvoiced':
                    invoice_line = invoice_line_obj.search(
                        cr, uid, [('invoice_id', '=', invoice.id),
                                  ('delivery_line', '=', False)],
                        context=context)
                    invoice.write({
                        'partner_id': picking.carrier_id.partner_id.id
                    })
                    if invoice_line:
                        invoice_line_obj.unlink(cr, uid, invoice_line)

                    invoice_line = self._prepare_shipping_invoice_line(
                        cr, uid, picking, invoice, context=context)

                    if invoice_line:
                        invoice_line_obj.create(cr, uid, invoice_line)

                    invoice_obj.button_compute(
                        cr, uid, [invoice.id], context=context,
                        set_total=(inv_type in ('out_invoice',
                                                'out_refund')))
                    picking.carrier_invoice_control = 'invoiced'

        picking = self.browse(cr, uid, key[1], context=context)
        if delivery_carrier and not picking.carrier_id.split_invoice and not delivey_invoices:
            for move in moves:
                key = (move.picking_id.partner_id.id, move.picking_id.id)
                for invoice_id in invoice_ids:
                    invoice = self.pool.get('account.invoice').browse(
                        cr, uid, invoice_id, context=context)
                    if invoice.origin == move.picking_id.name:
                        if key not in delivey_invoices:
                            delivey_invoices[key] = invoice

            for key, invoice in delivey_invoices.items():
                picking = self.browse(cr, uid, key[1], context=context)
                if picking.invoice_state == 'invoiced' and \
                        picking.carrier_invoice_control == '2binvoiced':
                    invoice_line = invoice_line_obj.search(
                        cr, uid, [('invoice_id', '=', invoice.id),
                                  ('delivery_line', '=', False)],
                        context=context)
                    invoice.write({
                        'partner_id': picking.carrier_id.partner_id.id
                    })

                    invoice_line = self._prepare_shipping_invoice_line(
                        cr, uid, picking, invoice, context=context)

                    if invoice_line:
                        invoice_line_obj.create(cr, uid, invoice_line)

                    invoice_obj.button_compute(
                        cr, uid, [invoice.id], context=context,
                        set_total=(inv_type in ('out_invoice',
                                                'out_refund')))
                    picking.carrier_invoice_control = 'invoiced'

        return invoice_ids

    def _prepare_shipping_invoice_line(
            self, cr, uid, picking, invoice, context=None):
        res = super(stock_picking, self)._prepare_shipping_invoice_line(
            cr, uid, picking, invoice, context=context)
        if res:
            res['delivery_line'] = True
            return res
        else:
            if not picking.carrier_id:
                return None
            carrier_obj = self.pool.get('delivery.carrier')
            grid_obj = self.pool.get('delivery.grid')
            currency_obj = self.pool.get('res.currency')
            grid_id = carrier_obj.grid_get(
                cr, uid, [picking.carrier_id.id], picking.partner_id.id,
                context=context)
            if not grid_id:
                raise Warning(
                    _('The carrier %s (id: %d) has no delivery grid!')
                    % (picking.carrier_id.name,
                       picking.carrier_id.id))
            quantity = sum([line.product_uom_qty for line in picking.
                            move_lines])
            price = grid_obj.get_price_from_picking(
                cr, uid, grid_id, invoice.amount_untaxed, picking.weight,
                picking.volume, quantity, context=context)
            if invoice.company_id.currency_id.id != invoice.currency_id.id:
                price = currency_obj.compute(
                    cr, uid, invoice.company_id.currency_id.id,
                    invoice.currency_id.id, price,
                    context=dict(context or {}, date=invoice.date_invoice))
                account_id = picking.carrier_id.product_id.property_account_income.id

            if not account_id:
                account_id = picking.carrier_id.product_id.categ_id. \
                    property_account_income_categ.id
                taxes = picking.carrier_id.product_id.taxes_id
                partner = picking.partner_id or False
                fp = invoice.fiscal_position or partner.property_account_position
            if partner:
                account_id = self.pool.get('account.fiscal.position') .\
                    map_account(cr, uid, fp, account_id)
                taxes_ids = self.pool.get('account.fiscal.position'). \
                    map_tax(cr, uid, fp, taxes, context=context)
            else:
                taxes_ids = [x.id for x in taxes]
            return {
                'name': picking.carrier_id.name,
                'invoice_id': invoice.id,
                'uos_id': picking.carrier_id.product_id.uos_id.id,
                'product_id': picking.carrier_id.product_id.id,
                'account_id': account_id,
                'price_unit': price,
                'quantity': 1,
                'invoice_line_tax_id': [(6, 0, taxes_ids)],
                'delivery_line': True
                }


class purchase_order(models.Model):

    _inherit = 'purchase.order'

    def action_picking_create(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be '
        'used for a single id at a time'
        res = super(purchase_order, self).action_picking_create(
            cr, uid, ids, context=context)
        purchase = self.browse(cr, uid, ids, context=context)
        if res:
            picking = self.pool.get('stock.picking').browse(
                cr, uid, res, context=context)
            picking.write({
                'carrier_invoice_control': purchase.carrier_id and picking.invoice_state or 'none'
            })
        return res
