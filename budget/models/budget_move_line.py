# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
from openerp.exceptions import Warning, ValidationError
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class BudgetMoveLine(models.Model):
    _name = "budget.move.line"
    _description = "Budget Move Line"

    @api.onchange('program_line_id')
    def on_change_program_line(self):
        for line in self:
            self.line_available = line.available_budget

    @api.multi
    def _compute(self, ignore_dist_ids=[]):
        amld = self.env['account.move.line.distribution']
        _fields = ['compromised', 'executed', 'reversed', 'reserved']
        res = {}
        for line in self:
            res[line.id] = {}
            executed = 0.0
            compromised = 0.0
            reserved = 0.0
            if line.state in ('executed', 'in_execution', 'transferred'):
                if line.type == 'opening':
                    executed = line.fixed_amount
                elif line.type in (
                        'manual_invoice_in', 'expense', 'invoice_in',
                        'payroll', 'manual'):
                    line_ids_bar = amld.search([
                        ('target_budget_move_line_id', '=', line.id),
                        ('account_move_line_type', '=', 'liquid')])
                    for bar_line in line_ids_bar:
                        if bar_line.id in ignore_dist_ids:
                            continue
                        executed += bar_line.distribution_amount
            void_line_ids_amld = amld.search([
                ('target_budget_move_line_id', '=', line.id),
                ('account_move_line_type', '=', 'void')])
            for void_line in void_line_ids_amld:
                if void_line.id in ignore_dist_ids:
                    continue
                reversed += void_line

            if line.previous_move_line_id:
                executed += line.previous_move_line_id.executed
                reversed += line.previous_move_line_id.reversed

            if line.state in ('compromised', 'executed', 'in_execution',
                              'transferred'):
                compromised = line.fixed_amount - executed - line.reversed
            if line.state == 'reserved':
                    reserved = line.fixed_amount - reversed

            line.excecuted = executed
            line.compromised = compromised
            line.reversed = reversed
            line.reserved = reserved
        return res

    @api.multi
    def compute(self, ignore_dist_ids=[]):
        return self._compute(ignore_dist_ids)

    @api.multi
    def _compute_modified(self):
        for line in self:
            total = 0.0
            if line.state == 'executed'and line.type == 'modification':
                total = line.fixed_amount
            line.canged = total

    @api.multi
    def _compute_extended(self):
        for line in self:
            total = 0.0
            if line.state == 'executed' and line.type == 'extension':
                total = line.fixed_amount
            line.extended = total

    @api.multi
    def _check_non_zero(self):
        for obj_bm in self:
            if (obj_bm.fixed_amount == 0.0 or obj_bm.fixed_amount is None)\
                    and obj_bm.standalone_move and obj_bm.state in (
                    'draft', 'reserved'):
                return False
        return True

    @api.one
    @api.constrains('fixed_amount', 'type')
    def _check_plan_state(self):
        if self.program_line_id.state != 'approved':
            if not self.from_migration:
                next_line = self.get_next_year_line()[self.id]
                if not next_line:
                    raise ValidationError(_("""
                The plan for this program line must be in approved state"""))
        return True

    @api.multi
    def _line_name(self):
        res = {}
        for line in self:
            res[line.id] = "%s \\ %s" % (line.budget_move_id.code, line.origin)
        return res

    origin = fields.Char(string='Origin', size=64)
    budget_move_id = fields.Many2one(
        'budget.move', 'Budget Move', required=True, ondelete='cascade')
    name = fields.Char(
        compute='_line_name', string='Name', readonly=True, store=True)
    code = fields.Char(related='origin', size=64, string='Origin')
    program_line_id = fields.Many2one(
        'budget.program.line', 'Program line', required=True)
    date = fields.Datetime(
        'Date created', required=True,
        default=lambda self: fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'
                                                            ))
    fixed_amount = fields.Float(
        'Original amount', digits=dp.get_precision('Account'))
    line_available = fields.Float(
        'Line available', digits=dp.get_precision('Account'), readonly=True)
    changed = fields.Float(
        compute='_compute_modified', string='Modified', readonly=True,
        store=True)
    extended = fields.Float(
        compute='_compute_extended', string='Extended', readonly=True,
        store=True)
    reserved = fields.Float(
        compute='_compute', string='Reserved', readonly=True, store=True)
    reversed = fields.Float(
        compute='_compute', string='Reversed', readonly=True, store=True,
        default=0.0)
    compromised = fields.Float(
        compute='_compute', string='Compromised', readonly=True, store=True)
    executed = fields.Float(
        compute='_compute', string='Executed', readonly=True, store=True)
    po_line_id = fields.Many2one(
        'purchase.order.line', string='Purchase order line')
    so_line_id = fields.Many2one(
        'sale.order.line', string='Sale order line')
    inv_line_id = fields.Many2one(
        'account.invoice.line', string='Invoice line')
    expense_line_id = fields.Many2one(
        'hr.expense.line', string='Expense line')
    tax_line_id = fields.Many2one(
        'account.invoice.tax', string='Invoice tax line')
    payslip_line_id = fields.Many2one(
        'hr.payslip.line', string='Payslip line')
    move_line_id = fields.Many2one(
        'account.move.line', string='Move line', )
    account_move_id = fields.Many2one(
        'account.move', string='Account Move', )
    type = fields.Char(
        related='budget_move_id.type', string='Type', readonly=True)
    state = fields.Char(
        related='budget_move_id.state', string='State',  readonly=True)
    # =======bugdet move line distributions
    budget_move_line_dist = fields.One2many(
        'account.move.line.distribution', 'target_budget_move_line_id',
        string='Budget Move Line Distributions')
    type_distribution = fields.Selection(
        related='budget_move_line_dist.type', string="Distribution type",
        selection=[('manual', 'Manual'), ('auto', 'Automatic')])
    # =======Payslip lines
    previous_move_line_id = fields.Many2one(
        'budget.move', 'Previous move line')
    from_migration = fields.Boolean(
        related='budget_move_id.from_migration', string='Transferred',
        readonly=True, default=False)

    @api.multi
    def get_next_year_line(self):
        res = {}
        for line in self:
            result = self.search([('previous_move_line_id', '=', line.id)])
            if result:
                res[line.id] = result[0]
            else:
                res[line.id] = None
        return res

    @api.model
    def create(self, vals):
        program_line = self.env['budget.program.line'].browse(
            vals['program_line_id'] or False)
        if program_line:
            if program_line.program_id.plan_id.state in ('cancel', 'closed'):
                raise Warning(_("""
        You cannot create a budget move line from an cancel or closed plan"""))
        return super(BudgetMoveLine, self).create(vals)

    @api.multi
    def write(self, vals):
        for bud_move_line in self:
            if bud_move_line.program_line_id.program_id.plan_id.state in (
                    'cancel', 'closed'):
                next_line =\
                    bud_move_line.get_next_year_line()[bud_move_line.id]
                if not next_line:
                    raise Warning(_("""
                You cannot create a budget move line with a canceled or
                closed plan"""))
        super(BudgetMoveLine, self).write(vals)
        next_year_lines = self.get_next_year_line()
        for line_id in next_year_lines.keys():
            if next_year_lines[line_id]:
                next_line = self.browse([next_year_lines[line_id]])[0]
                next_line.budget_move_id.recalculate_values()

    @api.multi
    def unlink(self):
        for bud_move_line in self:
            if bud_move_line.program_line_id.program_id.plan_id.state in (
                    'cancel', 'closed'):
                raise Warning(_("""
            You cannot create a budget move with a canceled or closed plan"""))
        super(BudgetMoveLine, self).unlink()
