# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class BudgetMove(models.Model):
    _name = "budget.move"
    _description = "Budget Move"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('reserved', 'Reserved'),
        ('compromised', 'Compromised'),
        ('in_execution', 'In Execution'),
        ('executed', 'Executed'),
        ('transferred', 'Transferred'),
        ('cancel', 'Canceled'),
    ]

    MOVE_TYPE = [
        ('invoice_in', _('Purchase invoice')),
        ('invoice_out', _('Sale invoice')),
        ('manual_invoice_in', _('Manual purchase invoice')),
        ('manual_invoice_out', _('Manual sale invoice')),
        ('expense', _('Expense')),
        ('payroll', _('Payroll')),
        ('manual', _('From account move')),
        ('modification', _('Modification')),
        ('extension', _('Extension')),
        ('opening', _('Opening'))
    ]

    @api.model
    def _check_manual(self):
        return True if self.env.context.get('standalone_move', False)\
            else False

    code = fields.Char('Code', size=64, )
    name = fields.Char(related='code')
    origin = fields.Char(
        'Origin', size=64, readonly=True,
        states={'draft': [('readonly', False)]})
    program_line_id = fields.Many2one(
        'budget.program.line', 'Program line', readonly=True,
        states={'draft': [('readonly', False)]})
    date = fields.Datetime(
        string='Date created', required=True, readonly=True,
        default=lambda self: fields.Datetime.now(),
        states={'draft': [('readonly', False)]})
    state = fields.Selection(
        STATE_SELECTION, 'State', readonly=True, select=True, default='draft',
        help="""
        The state of the move. A move that is still under planning is in a
        'Draft' state. Then the move goes to 'Reserved' state in order to
        reserve the designated amount. This move goes to 'Compromised' state
        when the purchase operation is confirmed. Finally goes to the
        'Executed' state where the amount is finally discounted from the budget
        available amount""")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id.id)
    fixed_amount = fields.Float(
        'Fixed amount', digits=dp.get_precision('Account'))
    standalone_move = fields.Boolean(
        'Standalone move', readonly=True, default=_check_manual,
        states={'draft': [('readonly', False)]})
    arch_reserved = fields.Float(
        'Original Reserved', digits=dp.get_precision('Account'))
    reserved = fields.Float(
        compute='_compute_reserved', string='Reserved', store=True)
    reversed = fields.Float(
        compute='_compute_reversed', string='Reversed', store=True)
    arch_compromised = fields.Float(
        'Original compromised', digits=dp.get_precision('Account'),)
    compromised = fields.Float(
        compute='_compute_compromised', string='Compromised', store=True)
    executed = fields.Float(
        compute='_compute_executed', string='Executed', store=True)
    account_invoice_ids = fields.One2many(
        'account.invoice', 'budget_move_id', string='Invoices')
    move_lines = fields.One2many(
        'budget.move.line', 'budget_move_id', string='Move lines')
    budget_move_line_dist = fields.One2many(
        'account.move.line.distribution',
        compute='_compute_move_lines_dist',
        string='Account Move Line Distribution')
    type = fields.Selection(
        selection='_select_types', string='Move Type', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    previous_move_id = fields.Many2one('budget.move', 'Previous move')
    from_migration = fields.Boolean('Created from migration')

    _defaults = {
        'company_id': lambda self: self.env.user.company_id.id
    }

    @api.one
    def _compute_move_lines_dist(self):
        dist_lines_ids = []
        for move in self.move_lines:
            for dist in move.budget_move_line_dist:
                dist_lines_ids.append(dist.id)
        self.budget_move_line_dist = list(set(dist_lines_ids))

    @api.multi
    def distribution_get(self):
        amld_obj = self.env['account.move.line.distribution']
        result = []
        search_ids = []
        for move in self:
            for bud_move_line in move.move_lines:
                search_ids = amld_obj.search(
                    [('target_budget_move_line_id', '=', bud_move_line.id)])
                result += search_ids._ids
        return result

    @api.one
    @api.depends('date', 'move_lines')
    def _compute_executed(self):
        total = 0.0
        for line in self.move_lines:
            total += line.executed
        self.executed = total

    @api.one
    @api.depends('date', 'move_lines')
    def _compute_compromised(self):
        total = 0.0
        for line in self.move_lines:
            total += line.compromised
        self.compromised = total

    # this function isn't call
    @api.one
    def _check_non_zero(self):
        if (self.fixed_amount == 0.0 or self.fixed_amount is None) and\
                self.standalone_move and\
                self.state in ('draft', 'reserved'):
            return False
        return True

    @api.one
    @api.depends('date', 'move_lines')
    def _compute_reserved(self):
        res_amount = 0
        if self.state == 'reserved':
            for line in self.move_lines:
                res_amount += line.reserved
        self.reserved = res_amount

    @api.one
    @api.depends('date', 'move_lines')
    def _compute_reversed(self):
        res_amount = 0
        for line in self.move_lines:
            res_amount += line.reversed
        self.reversed = res_amount

    @api.one
    def recalculate_values(self):
        move_fixed_total = 0.0
        for line in self.move_lines:
            line.write({'date': line.date})
            move_fixed_total += line.fixed_amount
        self.write({'date': self.date, 'fixed_amount': move_fixed_total})

    @api.model
    def _select_types(self):
        # In case that the move is created from the view
        # "view_budget_move_manual_form", modifies the selectable types
        # reducing them to modification, extension and opening
        if self.env.context.get('standalone_move', False):
            return [
                ('modification', _('Modification')),
                ('extension', _('Extension')),
                ('opening', _('Opening')),
            ]
        else:
            return [
                ('invoice_in', _('Purchase invoice')),
                ('invoice_out', _('Sale invoice')),
                ('manual_invoice_in', _('Manual purchase invoice')),
                ('manual_invoice_out', _('Manual sale invoice')),
                ('expense', _('Expense')),
                ('payroll', _('Payroll')),
                ('manual', _('From account move')),
                ('modification', _('Modification')),
                ('extension', _('Extension')),
                ('opening', _('Opening')),
            ]

    # come back here
    def _get_budget_moves_from_dist(self, cr, uid, ids, context=None):
        if ids:
            dist_obj = self.pool.get('account.move.line.distribution')
            dists = dist_obj.browse(cr, uid, ids, context=context)
            budget_move_ids = []
            for dist in dists:
                if dist.target_budget_move_line_id and\
                    dist.target_budget_move_line_id.budget_move_id and\
                    dist.target_budget_move_line_id.budget_move_id.id not in\
                        budget_move_ids:
                    budget_move_ids.append(
                        dist.target_budget_move_line_id.budget_move_id.id)
            return budget_move_ids
        return []

    def _get_budget_moves_from_lines(self, cr, uid, ids, context=None):
        if ids:
            lines_obj = self.pool.get('budget.move.line')
            lines = lines_obj.browse(cr, uid, ids, context=context)
            budget_move_ids = []
            for line in lines:
                if line.budget_move_id and\
                        line.budget_move_id.id not in budget_move_ids:
                    budget_move_ids.append(line.budget_move_id.id)
            return budget_move_ids
        return []

    # Store triggers for functional fields
    STORE = {
        'budget.move': (lambda self, cr, uid, ids, context={}: ids, [], 10),
        'budget.move.line': (_get_budget_moves_from_lines, [], 10),
        'account.move.line.distribution': (_get_budget_moves_from_dist, [], 10)
    }

    @api.model
    def transfer_to_next_year(self, move_ids, plan_id):
        MOVE_RELATED_MODELS = [
           'account.invoice',
           'account.move',
           'hr.expense.expense',
           'hr.payslip',
           'purchase.order',
        ]
        obj_bud_line = self.env['budget.move.line']
        for move in self.browse(move_ids):
            vals = {
                'origin': move.origin,
                'company_id': move.company_id.id,
                'fixed_amount': move.fixed_amount,
                'standalone_move': move.standalone_move,
                'arch_reserved': move.arch_reserved,
                'arch_compromised': move.arch_compromised,
                'type': move.type,
                'previous_move_id': move.id,
                'from_migration': True
            }
            new_move_id = self.create(vals)
            for line in move.move_lines:
                if line.executed != line.fixed_amount:
                    prog_line_id = line.program_line_id
                    next_prog_line =\
                        prog_line_id.get_next_year_line()[prog_line_id]
                    if next_prog_line:
                        line_vals = {
                           'origin': line.origin,
                           'budget_move_id': new_move_id,
                           'program_line_id': next_prog_line,
                           'date': line.date,
                           'fixed_amount': line.fixed_amount,
                           'line_available': line.line_available,
                           'po_line_id': line.po_line_id.id,
                           'so_line_id': line.so_line_id.id,
                           'inv_line_id': line.inv_line_id.id,
                           'expense_line_id': line.expense_line_id.id,
                           'tax_line_id': line.tax_line_id.id,
                           'payslip_line_id': line.payslip_line_id.id,
                           'move_line_id': line.move_line_id.id,
                           'account_move_id': line.account_move_id.id,
                           'previous_move_line_id': line.id
                        }
                        _new_move_line_id = obj_bud_line.create(line_vals)
                        fields_to_blank = {
                           'po_line_id': None,
                           'so_line_id': None,
                           'inv_line_id': None,
                           'expense_line_id': None,
                           'tax_line_id': None,
                           'payslip_line_id': None,
                           'move_line_id': None,
                           'account_move_id': None,
                        }
                        line.write(fields_to_blank)
            self.replace_budget_move(move.id, new_move_id, MOVE_RELATED_MODELS)
            new_move = self.browse(new_move_id)
            if move.state == 'compromised':
                new_move.signal_workflow('button_reserve')
                new_move.signal_workflow('button_compromise')
            if move.state == 'in_execution':
                new_move.signal_workflow('button_execute')

    @api.model
    def replace_budget_move(self, old_id, new_id, models):
        for model in models:
            obj = self.env[model]
            search_result = obj.search([('budget_move_id', '=', old_id)])
            search_result.write({'budget_move_id': new_id})

    @api.model
    def process_for_close(self, closeable_move_ids, plan_id):
        for move in self.browse(closeable_move_ids):
            if move.state in ('draft', 'reserved'):
                move.signal_workflow('button_cancel')
            if move.state in ('compromised', 'in_execution'):
                move.transfer_to_next_year(move._ids, plan_id)
                move.signal_workflow('button_transfer')

    @api.multi
    def _check_values(self):
        list_line_ids_repeat = []
        for move in self:
            if move.type in (
                    'invoice_in', 'manual_invoice_in', 'expense', 'opening',
                    'extension') and move.fixed_amount <= 0:
                return [False, _('The reserved amount must be positive')]
            if move.type in ('payroll') and move.fixed_amount < 0:
                return [False, _('The reserved amount must be positive')]
            if move.type in ('invoice_out', 'manual_invoice_out') and\
                    move.fixed_amount >= 0:
                return [False, _('The reserved amount must be negative')]
            if move.type in ('modifications') and move.fixed_amount != 0:
                return [False, _(
                    """The sum of addition and subtractions
                        from program lines must be zero""")]
            # Check if exist a repeated program_line
            if move.standalone_move:
                for line in move.move_lines:
                    list_line_ids_repeat.append(line.program_line_id.id)
                # Delete repeated items
                list_line_ids = list(set(list_line_ids_repeat))
                if len(list_line_ids_repeat) > len(list_line_ids):
                    return [False, _(
                        'Program lines in budget move lines cannot be repeated'
                    )]
            # Check amount for each move_line
            for line in move.move_lines:
                if line.type == 'extension':
                    if line.fixed_amount < 0:
                        return [False, _(
                            'An extension amount cannot be negative')]
                elif line.type == 'modification':
                    if (line.fixed_amount < 0) & (
                            line.program_line_id.available_budget <
                            abs(line.fixed_amount)):
                        return [False, _(
                            """The amount to substract from %s is greater
                            than the available""" % line.program_line_id.name)]
                elif line.type in (
                        'opening', 'manual_invoice_in', 'expense',
                        'invoice_in', 'manual'):
                    if line.program_line_id.available_budget <\
                            line.fixed_amount:
                        query = """SELECT id, fixed_amount FROM
                            budget_move_line WHERE id=%s"""
                        new_cr = self.pool.cursor()
                        new_cr.execute(query, (line.id,))
                        res_query = new_cr.dictfetchall()[0]
                        new_cr.close()
                        if (line.program_line_id.available_budget +
                                res_query['fixed_amount']) >=\
                                line.fixed_amount:
                            return [True, '']
                        return [False, _(
                            """The amount to substract from %s is greater
                            than the available""" % line.program_line_id.name)]
        return [True, '']

    @api.model
    def create(self, vals):
        bud_program_lines_obj = self.env['budget.program.line']
        bud_program_lines = []
        if 'code' not in vals.keys():
            vals['code'] = self.env['ir.sequence'].get('budget.move')
        elif vals['code'] is None or vals['code'] == '':
            vals['code'] = self.env['ir.sequence'].get('budget.move')
        # Extract program_line_id from values
        # (move_lines is a budget move line list)
        for bud_line in vals.get('move_lines', []):
            # position 3 is a dictionary, extract program_line_id value
            program_line_id = bud_line[2]['program_line_id']
            bud_program_lines.append(program_line_id)
        for line in bud_program_lines_obj.browse(bud_program_lines):
            if line.program_id.plan_id.state in ('closed', 'cancel'):
                raise Warning(_(
                    """You cannot create a budget move that have associated
                budget move lines with a closed or canceled budget plan"""))
        res = super(BudgetMove, self).create(vals)
        return res

    @api.one
    def write(self, vals):
        super(BudgetMove, self).write(vals)
        if self.state in ('reserved', 'draft') and self.standalone_move:
            res_amount = 0
            for line in self.move_lines:
                res_amount += line.fixed_amount
            vals['fixed_amount'] = res_amount
            return super(BudgetMove, self).write({'fixed_amount': res_amount})

    @api.one
    @api.onchange('move_lines')
    def on_change_move_line(self):
        res_amount = 0.0
        if self.standalone_move:
            res_amount = 0.0
            for line in self.move_lines:
                res_amount += line.fixed_amount
        self.fixed_amount = res_amount

    @api.one
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.one
    def action_reserve(self):
        # check positive or negative for different types of moves
        result = self._check_values()
        if result[0]:
            self.write({'state': 'reserved'})
            self.recalculate_values()
        else:
            raise Warning(result[1])
        return True

    @api.one
    def action_compromise(self):
        self.write({'state': 'compromised'})
        self.recalculate_values()
        self.write({'arch_compromised': self.compromised})
        return True

    @api.one
    def action_in_execution(self):
        result = self._check_values()
        if result[0]:
            self.write({'state': 'in_execution'})
            self.recalculate_values()
        else:
            raise Warning(result[1])
        return True

    @api.one
    def action_execute(self):
        self.write({'state': 'executed'})
        self.recalculate_values()
        return True

    @api.one
    def action_cancel(self):
        self.write({'state': 'cancel'})
        self.recalculate_values()
        return True

    @api.one
    def action_transfer(self):
        self.write({'state': 'transferred'})
        return True

    @api.multi
    def name_get(self):
        res = []
        if not self:
            return res
        for r in self.read(['code']):
            rec_name = '%s' % (r['code'])
            res.append((r['id'], rec_name))
        return res

    @api.one
    def is_executed(self):
        dist_obj = self.env['account.move.line.distribution']
        executed = 0.0
        void = 0.0
        if self.type in ('opening', 'extension', 'modification'):
            if self.state == 'in_execution':
                return True
        if self.type in ('manual_invoice_in', 'expense', 'invoice_in',
                         'payroll', 'manual'):
            distr_line_ids = []
            for line in self.move_lines:
                distr_line_ids += dist_obj.search(
                    [('target_budget_move_line_id', '=', line.id)])._ids
            for dist in dist_obj.browse(distr_line_ids):
                if dist.account_move_line_type == 'liquid':
                    executed += dist.distribution_amount
                elif dist.account_move_line_type == 'void':
                    void += dist.distribution_amount
            if executed == self.fixed_amount - void:
                return True
        return False

    @api.one
    def is_in_execution(self):
        dist_obj = self.env['account.move.line.distribution']
        executed = 0.0
        void = 0.0
        if self.type in ('opening', 'extension', 'modification'):
                return False
        if self.type in ('manual_invoice_in', 'expense', 'invoice_in',
                         'payroll', 'manual'):
            distr_line_ids = []
            for line in self.move_lines:
                distr_line_ids += dist_obj.search(
                    [('target_budget_move_line_id', '=', line.id)])._ids
            for dist in dist_obj.browse(distr_line_ids):
                if dist.account_move_line_type == 'liquid':
                    executed += dist.distribution_amount
                elif dist.account_move_line_type == 'void':
                    void += dist.distribution_amount
            if executed != self.fixed_amount - void:
                return True
        return False

    @api.one
    def dummy_button(self):
        return True

    @api.multi
    def unlink(self):
        for move in self:
            if move.state != 'draft':
                raise Warning(_(
                    'Orders in state other than draft cannot be deleted'))
            for line in move.move_lines:
                if line.program_line_id.program_id.plan_id.state in (
                        'approved', 'closed'):
                    raise Warning(_("""
                    You cannot delete a budget move budget move that have
                associated budget lines with a approved or closed budge
                plan"""))
        super(BudgetMove, self).unlink()
