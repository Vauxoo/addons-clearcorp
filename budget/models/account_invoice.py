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
        'budget.move', string='Budget move', readonly=True)
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
        bud_move_obj = self.env['budget.move']
        _type = False
        if self.type in ('in_invoice', 'out_refund'):
            _type = 'manual_invoice_in'
        if self.type in ('out_invoice', 'in_refund'):
            _type = 'manual_invoice_out'
        move_id = bud_move_obj.create({'type': _type})
        return move_id

    @api.one
    def update_budget_move(self):
        _type = False
        if self.type in ('in_invoice', 'out_refund'):
            _type = 'manual_invoice_in'
        if self.type in ('out_invoice', 'in_refund'):
            _type = 'manual_invoice_out'
        self.budget_move_id.write({'type': _type})
        move_ids = [(2, x.id)for x in self.budget_move_id.move_lines]
        if move_ids:
            self.budget_move_id.write({'move_lines': move_ids})

    @api.model
    def create_budget_move_line_from_invoice(self, line_id, is_tax=False):
        inv_line_obj = self.env['account.invoice.line']
        bud_line_obj = self.env['budget.move.line']
        fixed_amount = 0.0
        invoice_line = inv_line_obj.browse(line_id)
        invoice = invoice_line.invoice_id
        move_id = invoice.budget_move_id
        refund = False
        vals = {
            'budget_move_id': move_id.id,
            'origin': invoice_line.name,
            'program_line_id': invoice_line.program_line_id.id,
            'account_move_id': invoice.move_id.id
        }
        if invoice.type in ('in_invoice', 'out_refund'):
            fixed_amount = invoice_line.price_subtotal
            vals['inv_line_id'] = line_id
            if invoice.type == 'out_refund':
                refund = True
        if invoice.type in ('out_invoice', 'in_refund'):
            # should be negative because it is an income
            fixed_amount = invoice_line.price_subtotal * -1
            vals['inv_line_id'] = line_id
            if invoice.type == 'in_refund':
                refund = True
        vals['fixed_amount'] = fixed_amount
        bud_line = bud_line_obj.create(vals)
        budget_type = 'void' if refund else 'budget'
        invoice.move_id.write({'budget_type': budget_type})
        return bud_line

    @api.model
    def create_budget_move_line_from_tax(self, line_id):
        acc_inv_tax_obj = self.env['account.invoice.tax']
        bud_line_obj = self.env['budget.move.line']
        fixed_amount = 0.0
        tax_line = acc_inv_tax_obj.browse(line_id)
        invoice = tax_line.invoice_id
        move_id = invoice.budget_move_id
        refund = False
        vals = {
            'budget_move_id': move_id.id,
            'origin': tax_line.name,
            'account_move_id': invoice.move_id.id
        }
        if invoice.type in ('in_invoice', 'out_refund'):
            fixed_amount = tax_line.tax_amount
            vals['tax_line_id'] = line_id
            if invoice.type == 'out_refund':
                refund = True
        if invoice.type in ('out_invoice', 'in_refund'):
            fixed_amount = tax_line.tax_amount * -1
            vals['tax_line_id'] = line_id
            if invoice.type == 'in_refund':
                refund = True
        invoice_lines = tax_line.invoice_id.invoice_line
        for inv_line in invoice_lines:
            if tax_line.base_amount == inv_line.price_subtotal:
                vals['program_line_id'] = inv_line.program_line_id.id
        vals['fixed_amount'] = fixed_amount
        bud_line = bud_line_obj.create(vals)
        budget_type = 'void' if refund else 'budget'
        invoice.move_id.write({'budget_type': budget_type})
        return bud_line

    @api.one
    def invoice_validate(self):
        obj_bud_move_line = self.env['budget.move.line']
        validate_result = super(account_invoice, self).invoice_validate()
        if not self._check_from_order():
            move_id = self.budget_move_id if self.budget_move_id else\
                self.create_budget_move()
            self.write({'budget_move_id': move_id})
            # creating budget move lines per invoice line
            for line in self.invoice_line:
                if not line.invoice_id.from_order:
                    self.create_budget_move_line_from_invoice(line.id)
            # creating budget move lines per tax line
            for line in self.tax_line:
                if not line.invoice_id.from_order:
                    self.create_budget_move_line_from_tax(line.id)
            move_id.write(
                {'origin': self.name,
                 'fixed_amount': self.amount_total,
                 'arch_compromised': self.amount_total})
            # Associating
            bud_lines_ids = obj_bud_move_line.search(
                [('budget_move_id', '=', move_id.id)])
            bud_lines = obj_bud_move_line.browse(bud_lines_ids)
            move_lines = self.move_id.line_id
            assigned_mov_lines = []
            for bud_line in bud_lines:
                for move_line in move_lines:
                    fixed_amount = abs(move_line.debit - move_line.credit) or\
                        abs(move_line.amount_currency)
                    account_id = 0
                    if bud_line.inv_line_id and\
                            bud_line.inv_line_id.account_id:
                        account_id = bud_line.inv_line_id.account_id.id
                    elif bud_line.tax_line_id and\
                            bud_line.tax_line_id.account_id:
                        account_id = bud_line.tax_line_id.account_id.id
                    if move_line.id not in assigned_mov_lines and\
                            bud_line.origin.find(move_line.name) != -1 and\
                            bud_line.fixed_amount == fixed_amount and \
                            account_id == move_line.account_id.id:
                        bud_line.write({'move_line_id': move_line.id})
                        assigned_mov_lines.append(move_line.id)
            move_id.signal_workflow('button_execute')
        else:
            for inv_line in self.invoice_line:
                bud_line = obj_bud_move_line.search(
                    [('inv_line_id', '=', inv_line.id)])[0]
                move_id = bud_line.budget_move_id
                move_lines = self.move_id.line_id
                assigned_mov_lines = []
                for move_line in move_lines:
                    fixed_amount = abs(move_line.debit - move_line.credit) or\
                        abs(move_line.amount_currency)
                    account_id = 0
                    if bud_line.inv_line_id and\
                            bud_line.inv_line_id.account_id:
                        account_id = bud_line.inv_line_id.account_id.id
                    elif bud_line.tax_line_id and\
                            bud_line.tax_line_id.account_id:
                        account_id = bud_line.tax_line_id.account_id.id
                    if move_line.id not in assigned_mov_lines and\
                            bud_line.fixed_amount == fixed_amount and \
                            account_id == move_line.account_id.id:
                        bud_line.write({'move_line_id': move_line.id})
                        assigned_mov_lines.append(move_line.id)
            move_id.signal_workflow('button_execute')
        return validate_result

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'budget_move_id': False})
        return super(account_invoice, self).copy(default)


class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    program_line_id = fields.Many2one('budget.program.line', 'Program line')
    invoice_from_order = fields.Boolean(
        compute='_check_from_order', string='From order')
    line_available = fields.Float(
        'Line available', digits=dp.get_precision('Account'), readonly=True)
    subtotal_discounted_taxed = fields.Float(
        compute='_subtotal_discounted_taxed',
        digits=dp.get_precision('Account'), string='Subtotal')

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

    @api.one
    def write(self, vals):
        result = super(AccountInvoiceLine, self).write(vals)
        self.invoice_id.write({'name': self.invoice_id.name})
        return result
