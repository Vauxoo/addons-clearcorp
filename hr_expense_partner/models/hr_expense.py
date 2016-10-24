# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrExpenseExpense(models.Model):
    _name = "hr.expense"
    _inherit = 'hr.expense'

    def _prepare_move_line(self, line):
        res = super(HrExpenseExpense, self)._prepare_move_line(line)
        if self.product_id:
            account = \
                self.product_id.product_tmpl_id._get_product_accounts(
                )['expense'].id
        else:
            account = self.env['ir.property'].with_context(
                force_company=self.company_id.id).get(
                'property_account_expense_categ_id', 'product.category').id
        if res['account_id'] != account:
            res['partner_id'] = self.supplier_id.id
        return res

    supplier_id = fields.Many2one(
        'res.partner', string='Supplier', readonly=True,
        states={'draft': [('readonly', False)]}, index=True)
    supplier_reference = fields.Char(
        string='Supplier Reference', readonly=True,
        states={'draft': [('readonly', False)]}, index=True)
