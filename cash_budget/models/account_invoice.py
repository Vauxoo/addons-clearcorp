# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import openerp.addons.decimal_precision as dp
from openerp import models, fields, api


class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    @api.one
    def _check_from_order(self):
        if self:
            return self.from_order
        else:
            res = self.env.context.get('from_order', False)
            return res

    budget_move_id = fields.Many2one(
        'cash.budget.move', string='Budget move', readonly=True)
    from_order = fields.Boolean('From order', default=_check_from_order)

    @api.one
    def action_cancel(self):
        res = super(account_invoice, self).action_cancel()
        if self.budget_move_id:
            self.budget_move_id.signal_workflow('button_cancel')
        return res

    @api.one
    def action_cancel_draft(self):
        res = super(account_invoice, self).action_cancel_draft()
        if self.budget_move_id:
            self.budget_move_id.signal_workflow('button_draft')
        return res

    @api.one
    def create_budget_move(self):
        if self.type in ['in_invoice', 'out_invoice']:
            bud_move_obj = self.env['cash.budget.move']
            _type = False
            if self.type == 'in_invoice':
                _type = 'manual_invoice_in'
            else:
                _type = 'manual_invoice_out'
            move_id = bud_move_obj.create({
                'type': _type,
                'origin': self.number,
                'fixed_amount': self.amount_total,
                'arch_compromised': self.amount_total})
            return move_id
        return False

    @api.one
    def update_budget_move(self):
        if self.type in ['in_invoice', 'out_invoice']:
            _type = False
            if self.type == 'in_invoice':
                _type = 'manual_invoice_in'
            else:
                _type = 'manual_invoice_out'
            self.budget_move_id.write({'type': _type})
            move_ids = [(2, x.id)for x in self.budget_move_id.move_lines]
            if move_ids:
                self.budget_move_id.write({'move_lines': move_ids})
            return True
        return False

    @api.model
    def create_budget_move_line_from_invoice(self, line_id, is_tax=False):
        inv_line_obj = self.env['account.invoice.line']
        bud_line_obj = self.env['cash.budget.move.line']
        fixed_amount = 0.0
        invoice_line = inv_line_obj.browse(line_id)
        if invoice_line.invoice_id.type not in ['in_refund', 'out_refund']:
            invoice = invoice_line.invoice_id
            move_id = invoice.budget_move_id
            vals = {
                'budget_move_id': move_id.id,
                'origin': invoice_line.name,
                'program_line_id': invoice_line.program_line_id.id,
                'account_move_id': invoice.move_id.id
            }
            if invoice.type == 'in_invoice':
                fixed_amount = invoice_line.price_subtotal
                vals['inv_line_id'] = line_id
            else:
                # should be negative because it is an income
                fixed_amount = invoice_line.price_subtotal * -1
                vals['inv_line_id'] = line_id
            vals['fixed_amount'] = fixed_amount
            bud_line = bud_line_obj.create(vals)
            return bud_line
        return False

    @api.model
    def create_budget_move_line_from_tax(self, line_id):
        acc_inv_tax_obj = self.env['account.invoice.tax']
        bud_line_obj = self.env['cash.budget.move.line']
        fixed_amount = 0.0
        tax_line = acc_inv_tax_obj.browse(line_id)
        if tax_line.invoice_id.type not in ['in_refund', 'out_refund']:
            invoice = tax_line.invoice_id
            move_id = invoice.budget_move_id
            vals = {
                'budget_move_id': move_id.id,
                'origin': tax_line.name,
                'account_move_id': invoice.move_id.id,
                'tax_line_id': line_id
            }
            if invoice.type == 'in_invoice':
                fixed_amount = tax_line.tax_amount
            else:
                fixed_amount = tax_line.tax_amount * -1
            vals['fixed_amount'] = fixed_amount

            # es necesario cambiar la forma en que se generan los
            # account_invoice_tax para que sea haga uno por cada combinacion de tax
            # y budget_program_line
            """
            invoice_lines = tax_line.invoice_id.invoice_line
            for inv_line in invoice_lines:
                if tax_line.base_amount == inv_line.price_subtotal:
                    vals['program_line_id'] = inv_line.program_line_id.id"""
            bud_line = bud_line_obj.create(vals)
            return bud_line
        return False

    @api.multi
    def action_move_create(self):
        for inv in self:
            if not inv._check_from_order() and not inv.budget_move_id\
                    and inv.type not in ['in_refund', 'out_refund']:
                inv.budget_move_id = inv.create_budget_move()
        res = super(account_invoice, self).action_move_create()
        for inv in self:
            if inv.type in ['in_refund', 'out_refund']:
                inv.move_id.budget_type = 'void'
            else:
                inv.move_id.budget_type = 'budget'
                inv.budget_move_id.signal_workflow('button_execute')
                inv.budget_move_id.recalculate_values()
        return res

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(account_invoice, self).line_get_convert(line, part, date)
        if 'budget_move_lines' in line:
            res.update({
                'budget_move_lines': line.get('budget_move_lines', False),
                'budget_program_line': line.get('budget_program_line', False)
            })
        return res

    @api.multi
    def action_number(self):
        res = super(account_invoice, self).action_number()
        for inv in self:
            if inv.budget_move_id and inv.budget_move_id.type in [
                    'manual_invoice_in', 'manual_invoice_out']:
                inv.budget_move_id.origin = inv.number
        return res

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'budget_move_id': False})
        return super(account_invoice, self).copy(default)


class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    program_line_id = fields.Many2one(
        'cash.budget.program.line', 'Program line')
    invoice_from_order = fields.Boolean(
        compute='_check_from_order', string='From order')
    line_available = fields.Float(
        'Line available', digits=dp.get_precision('Account'), readonly=True,
        compute='_compute_line_available', store=True)
    subtotal_discounted_taxed = fields.Float(
        compute='_subtotal_discounted_taxed',
        digits=dp.get_precision('Account'), string='Subtotal')
    budget_move_line_ids = fields.One2many(
        'cash.budget.move.line', 'inv_line_id', string='Budget Move Lines')

    @api.one
    @api.depends('program_line_id')
    def _compute_line_available(self):
        res_amount = 0.0
        for line in self.program_line_id:
            res_amount += line.available_budget
        self.line_available = res_amount

    @api.one
    def _check_from_order(self):
        self.invoice_from_order = self.invoice_id.from_order\
            if self.invoice_id else self.env.context.get('from_oder', False)

    @api.onchange('program_line_id')
    def on_change_program_line(self):
        for line in self.program_line_id:
            self.line_available = line.available_budget

    @api.onchange('account_id')
    def on_change_account_id(self):
        if self.account_id:
            if self.account_id.default_budget_program_line.id:
                self.program_line_id =\
                    self.account_id.default_budget_program_line.id

    @api.one
    def _subtotal_discounted_taxed(self):
        if self.discount > 0:
            price_unit_discount = self.price_unit - (self.price_unit *
                                                     (self.discount / 100))
        else:
            price_unit_discount = self.price_unit
        # -----taxes---------------#
        # taxes must be calculated with unit_price - discount
        amount_discounted_taxed = self.invoice_line_tax_id.compute_all(
            price_unit_discount, self.quantity, self.product_id.id,
            self.invoice_id.partner_id)['total_included']
        self.subtotal_discounted_taxed = amount_discounted_taxed

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        if line.invoice_id.type in ['in_invoice', 'out_invoice']:
            bmls = line.budget_move_line_ids.ids
            if not bmls and line.purchase_line_id:
                bmls = line.purchase_line_id.budget_move_line_ids.ids
            if not bmls:
                bmls = self.env['account.invoice'].\
                        create_budget_move_line_from_invoice(line.id).ids
            res['budget_move_lines'] = [(6, 0, bmls)]
            res['budget_program_line'] = line.program_line_id.id
        return res

    @api.one
    def write(self, vals):
        result = super(AccountInvoiceLine, self).write(vals)
        self.invoice_id.write({'name': self.invoice_id.name})
        return result


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    # Hay que probar si viene de un PO para utilizar los budget_move_lines
    #  que ya existen y no crear nuevos
    @api.model
    def move_line_get(self, invoice_id):
        res = super(AccountInvoiceTax, self).move_line_get(invoice_id)
        if self.env['account.invoice'].browse(invoice_id).type in\
                ['in_invoice', 'out_invoice']:
            checked_lines = []
            for aml in res:
                aits = self.search([
                    ('id', 'not in', checked_lines),
                    ('invoice_id', '=', invoice_id),
                    ('name', '=', aml['name']),
                    ('amount', '=', aml['price_unit']),
                    ('account_id', '=', aml['account_id']),
                    ('tax_code_id', '=', aml['tax_code_id']),
                    ('tax_amount', '=', aml['tax_amount']),
                    ('account_analytic_id', '=', aml['account_analytic_id'])])
                if aits:
                    bml = self.env['account.invoice']\
                        .create_budget_move_line_from_tax(aits[0].id)
                    aml['budget_move_lines'] = [(4, bml.id)]
                    checked_lines.append(aits[0].id)
        return res
