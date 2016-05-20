# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time


class budget_move_line(models.Model):
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
            if line.state == 'executed':
                if line.type == 'modification':
                    total = line.fixed_amount
            line.canged = total

    def _compute_extended(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        lines = self.browse(cr, uid, ids,context=context) 
        for line in lines:
            total = 0.0
            if line.state == 'executed':
                if line.type == 'extension':
                    total = line.fixed_amount
            res[line.id]= total 
        return res
    
    def _check_non_zero(self, cr, uid, ids, context=None):
        for obj_bm in  self.browse(cr, uid, ids, context=context):
            if (obj_bm.fixed_amount == 0.0 or obj_bm.fixed_amount == None) and obj_bm.standalone_move == True and obj_bm.state in ('draft','reserved'):
                return False
        return True
    
    def _check_plan_state(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            if line.program_line_id.state != 'approved':
                if not line.from_migration:
                    next_line = self.get_next_year_line(cr, uid, [line.id], context=context)[line.id]
                    if not next_line:
                        return False
        return True

    def _line_name(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
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

    _constraints = [
        (_check_plan_state, 'Error!\n The plan for this program line must be in approved state', ['fixed_amount','type']),
        ]
    
    def get_next_year_line(self, cr, uid, ids, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            result = self.search(cr, uid, [('previous_move_line_id','=',line.id)],context=context)
            if result:
                res[line.id]=result[0]
            else:
                res[line.id]=None
        return res
    
    def create(self, cr, uid, vals, context={}):
        program_line_obj = self.pool.get('budget.program.line')
        program_line = program_line_obj.browse(cr, uid, [vals['program_line_id']],context=context)[0]
        if program_line.program_id.plan_id.state in ('cancel', 'closed'):
            raise osv.except_osv(_('Error!'), _('You cannot create a budget move line from an cancel or closed plan'))
        return super(budget_move_line, self).create(cr, uid, vals, context)
       
    def write(self, cr, uid, ids, vals, context=None):
        bud_move_obj = self.pool.get('budget.move')
        
        for bud_move_line in self.browse(cr, uid, ids, context=context):
             if bud_move_line.program_line_id.program_id.plan_id.state in ('cancel','closed'):
                 next_line = self.get_next_year_line(cr, uid, [bud_move_line.id], context=context)[bud_move_line.id]
                 if not next_line:
                     raise osv.except_osv(_('Error!'), _('You cannot create a budget move line with a canceled or closed plan'))
            
        super(budget_move_line, self).write(cr, uid, ids, vals, context=context)
        
        next_year_lines = self.get_next_year_line(cr, uid, ids, context=context)
        for line_id in next_year_lines.keys():
            if next_year_lines[line_id]:
                next_line =self.browse(cr, uid, [next_year_lines[line_id]], context=context)[0]
                bud_move_obj.recalculate_values(cr, uid,[next_line.budget_move_id.id], context=context)    

    @api.multi
    def unlink(self):
        for bud_move_line in self:
            if bud_move_line.program_line_id.program_id.plan_id.state in (
                    'cancel', 'closed'):
                raise Warning(_("""
            You cannot create a budget move with a canceled or closed plan"""))
        super(budget_move_line, self).unlink()
