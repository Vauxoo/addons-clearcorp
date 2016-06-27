# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.translate import _
from openerp.exceptions import Warning
from openerp import models, fields, api


class HRExpenseExpense(models.Model):
    _name = "hr.expense.expense"
    _inherit = 'hr.expense.expense'

    budget_move_id = fields.Many2one(
        'cash.budget.move', 'Budget move', readonly=True)

    @api.model
    def create_budget_move_line(self, line_id):
        exp_line_obj = self.env['hr.expense.line']
        bud_line_obj = self.env['cash.budget.move.line']
        expense_line = exp_line_obj.browse(line_id)
        expense = expense_line.expense_id
        move_id = expense.budget_move_id
        fixed_amount = expense_line.total_amount
        bud_line = bud_line_obj.create({
            'budget_move_id': move_id.id,
            'origin': expense_line.name,
            'program_line_id': expense_line.program_line_id.id,
            'fixed_amount': fixed_amount,
            'expense_line_id': line_id
        })
        return bud_line

    @api.model
    def create(self, vals):
        exp_id = super(HRExpenseExpense, self).create(vals)
        move_id = exp_id.create_budget_move()[0]
        exp_id.write({'budget_move_id': move_id.id})
        expense_amount = exp_id.amount

        for line in exp_id.line_ids:
            self.create_budget_move_line(line.id)
        move_id.write({'fixed_amount': expense_amount})
        move_id.signal_workflow('button_reserve')
        return exp_id

    @api.one
    def write(self, vals):
        result = super(HRExpenseExpense, self).write(vals)
        if self.budget_move_id and self.budget_move_id.state != 'draft':
            self.budget_move_id.write({'fixed_amount': self.amount})
            self.budget_move_id.recalculate_values()
        if 'state' in vals:
            if vals['state'] == 'paid':
                self.budget_move_id.action_execute()
        return result

    @api.one
    def create_budget_move(self):
        bud_move_obj = self.env['cash.budget.move']
        move_id = bud_move_obj.create({'type': 'expense'})
        return move_id

    @api.one
    def expense_confirm(self):
        super(HRExpenseExpense, self).expense_confirm()
        self.write({'budget_move_id': self.budget_move_id.id})

    @api.one
    def expense_canceled(self):
        super(HRExpenseExpense, self).expense_canceled()
        self.budget_move_id.signal_workflow('button_cancel')
        self.budget_move_id.recalculate_values()

    @api.one
    def expense_draft(self):
        self.write({'state': 'draft'})
        if self.budget_move_id:
            self.budget_move_id.signal_workflow('button_draft')
            self.budget_move_id.signal_workflow('button_reserve')
            self.budget_move_id.recalculate_values()

    @api.one
    def expense_accept(self):
        self.budget_move_id.signal_workflow('button_compromise')
        self.budget_move_id.recalculate_values()
        return super(HRExpenseExpense, self).expense_accept()

    @api.one
    def action_receipt_create(self):
        mov_line_obj = self.env['cash.budget.move.line']
        # result = super(HRExpenseExpense, self).action_receipt_create()
        self.account_move_id.write({'budget_type': 'budget'})
        self.budget_move_id.move_lines.write(
            {'account_move_id': self.account_move_id.id})
        self.budget_move_id.signal_workflow('button_compromise')
        self.budget_move_id.signal_workflow('button_execute')
        exp_lines = self.line_ids
        # taxes_per_line = self.tax_per_exp_line(exp_lines)
        taxes_per_line = {}
        # list of associated expense lines with account move lines
        assigned_exp_lines = []
        # list of expense lines whose tax has been associated with account move
        # lines
        assigned_tax_exp_lines = []
        for acc_move_line in self.account_move_id.line_id:
            for exp_line in exp_lines:
                exp_acc = exp_line.product_id.property_account_expense or \
                    exp_line.product_id.categ_id.property_account_expense_categ
                exp_name = exp_line.name
                exp_amount = exp_line.total_amount
                acc_move_line_amount = \
                    abs(acc_move_line.debit - acc_move_line.credit) or \
                    abs(acc_move_line.amount_currency)
                if exp_name.find(acc_move_line.name) != -1 and \
                        exp_amount == acc_move_line_amount and \
                        exp_acc.id == acc_move_line.account_id.id and \
                        exp_line.id not in assigned_exp_lines:
                    bud_move_id = mov_line_obj.search(
                        [('expense_line_id', '=', exp_line.id)])
                    if bud_move_id:
                        bud_move_id.write({'move_line_id': acc_move_line.id})
                        assigned_exp_lines.append(exp_line.id)
                if not acc_move_line.product_id:
                    if exp_line.id not in assigned_tax_exp_lines:
                        exp_line_taxes = taxes_per_line.get(exp_line.id, [])
                        for tax_amount in exp_line_taxes:
                            fixed_amount = \
                                abs(acc_move_line.debit -
                                    acc_move_line.credit) or \
                                abs(acc_move_line.amount_currency)
                            if fixed_amount == tax_amount:
                                mov_line_obj.create({
                                    'budget_move_id':
                                        exp_line.expense_id.budget_move_id.id,
                                    'origin':
                                        _('Tax of: ') + exp_line.name[:54],
                                    'program_line_id':
                                        exp_line.program_line_id.id,
                                    'fixed_amount': abs(
                                        acc_move_line.debit -
                                        acc_move_line.credit) or
                                        abs(acc_move_line.amount_currency),
                                    # 'expense_line_id': line_id,
                                    'move_line_id': acc_move_line.id,
                                    'account_move_id': self.account_move_id.id
                                })
                                assigned_tax_exp_lines.append(exp_line.id)

        return True

    @api.model
    def tax_per_exp_line(self, expense_lines):
        res = []
        tax_obj = self.env['account.tax']
        cur_obj = self.env['res.currency']
        mapping = {}
        for line in expense_lines:
            exp = line.expense_id
            company_currency = exp.company_id.currency_id.id
            mres = self.move_line_get_item(line)
            if not mres:
                continue
            res.append(mres)
            tax_code_found = False
            # Calculate tax according to default tax on product
            taxes = []
            # Taken from product_id_onchange in account.invoice
            if line.product_id:
                fposition_id = False
                fpos_obj = self.env['account.fiscal.position']
                fpos = fposition_id and fpos_obj.browse(fposition_id) or False
                product = line.product_id
                taxes = product.supplier_taxes_id
                # If taxes are not related to the product, maybe they are in
                # the account
                if not taxes:
                    acc_exp = product.property_account_expense.id
                    if not acc_exp:
                        acc_exp =\
                            product.categ_id.property_account_expense_categ.id
                    acc_exp = fpos_obj.map_account(fpos, acc_exp)
                    taxes = acc_exp and self.env['account.account'].browse(
                        acc_exp).tax_ids or False
                _tax_id = fpos_obj.map_tax(fpos, taxes)
            if not taxes:
                continue
            # Calculating tax on the line and creating move?
            for tax in tax_obj.compute_all(
                    taxes, line.unit_amount, line.unit_quantity,
                    line.product_id, exp.user_id.partner_id)['taxes']:
                line_tax_amounts = []
                tax_code_id = tax['base_code_id']
                tax_amount = line.total_amount * tax['base_sign']
                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(line))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True
                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] =\
                    cur_obj.with_context(date=exp.date_confirm).compute(
                    exp.currency_id.id, company_currency, tax_amount,
                    context={'date': exp.date_confirm})
                is_price_include = tax_obj.browse(tax['id']).read(
                    ['price_include'])['price_include']
                if is_price_include:
                    # We need to deduce the price for the tax
                    res[-1]['price'] =\
                        res[-1]['price'] - (
                        tax['amount'] * tax['base_sign'] or 0.0)
                assoc_tax = {
                    'type': 'tax',
                    'name': tax['name'],
                    'price_unit': tax['price_unit'],
                    'quantity': 1,
                    'price':  tax['amount'] * tax['base_sign'] or 0.0,
                    'account_id':
                        tax['account_collected_id'] or mres['account_id'],
                    'tax_code_id': tax['tax_code_id'],
                    'tax_amount': tax['amount'] * tax['base_sign'],
                }
                line_tax_amounts.append(assoc_tax['tax_amount'])
                res.append(assoc_tax)
            mapping[line.id] = line_tax_amounts
        return mapping

    @api.one
    @api.onchange('currency_id')
    def on_change_currency(self, currency_id):
        if self:
            raise Warning(_(
                "Budget uses the currency of the company, if you use other, "
                "you should change the unit price"))

    @api.one
    def action_move_create(self):
        res = super(HRExpenseExpense, self).action_move_create()
        self.action_receipt_create()
        return res


class HRExpenseLine(models.Model):
    _name = "hr.expense.line"
    _inherit = 'hr.expense.line'

    program_line_id = fields.Many2one(
        'cash.budget.program.line', 'Program line')
    line_available = fields.Float(
        compute='_check_available', string='Line available')

    @api.onchange('program_line_id')
    def on_change_program_line(self):
        if self.program_line_id:
            self.line_available = self.program_line_id.available_budget

    @api.one
    @api.constrains('product_id')
    def _check_no_taxes(self):
        message = _(
            "There is a tax defined for this product, its account or the "
            "account of the product category. The tax must be included in the "
            "price of the expense product.")
        product = self.product_id
        if product.supplier_taxes_id:
            raise Warning(_(message))
        if product.property_account_expense and\
                product.property_account_expense.tax_ids:
            raise Warning(_(message))
        elif product.categ_id.property_account_expense_categ and\
                product.categ_id.property_account_expense_categ.tax_ids:
            raise Warning(_(message))

    @api.one
    def _check_available(self):
        bud_line_obj = self.env['cash.budget.move.line']
        bud_line_ids = bud_line_obj.search([('expense_line_id', '=', self.id)])
        for bud_line in bud_line_ids:
            self.line_available = bud_line.program_line_id.available_budget

    @api.one
    def create_budget_move_line(self, line_id):
        exp_line_obj = self.env['hr.expense.line']
        bud_line_obj = self.env['cash.budget.move.line']
        expense_line = exp_line_obj.browse(line_id)
        expense = expense_line
        move_id = expense.budget_move_id
        fixed_amount = expense_line.total_amount
        bud_line = bud_line_obj.create({
            'budget_move_id': move_id.id,
            'origin': expense_line.name,
            'program_line_id': expense_line.program_line_id.id,
            'fixed_amount': fixed_amount,
            'expense_line_id': line_id
        })
        move_id.recalculate_values()
        return bud_line

    @api.model
    def create(self, vals):
        exp_obj = self.env['hr.expense.expense']
        exp_line_id = super(HRExpenseLine, self).create(vals)
        exp_id = vals['expense_id']
        for expense in exp_obj.browse(exp_id):
            if expense.budget_move_id:
                _bud_line_id = self.create_budget_move_line(exp_line_id)
        return exp_line_id

    @api.one
    def write(self, vals):
        bud_line_obj = self.env['cash.budget.move.line']
        write_result = True
        bud_line_dict = {}
        if 'unit_amount' in vals.keys() or 'program_line_id' in vals.keys() or\
                'name' in vals.keys():
            if 'unit_amount' in vals.keys():
                bud_line_dict['fixed_amount'] = vals['unit_amount']
            if 'program_line_id' in vals.keys():
                bud_line_dict['program_line_id'] = vals['program_line_id']
            if 'name' in vals.keys():
                bud_line_dict['origin'] = vals['name']
            write_result = super(HRExpenseLine, self).write(vals)
            bud_line_ids = bud_line_obj.search(
                [('expense_line_id', '=', self.id)])
            for bud_line in bud_line_ids:
                bud_line.write(bud_line_dict)
                result = bud_line._check_values()
                if not result[0]:
                    raise Warning(result[1])
        else:
            write_result = super(HRExpenseLine, self).write(vals)
        return write_result
