# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time


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

    code = fields.Char('Code', size=64, )
    name = fields.Char(related='code')
    origin = fields.Char(
        'Origin', size=64, readonly=True,
        states={'draft': [('readonly', False)]})
    program_line_id = fields.Many2one(
        'budget.program.line', 'Program line', readonly=True,
        states={'draft': [('readonly', False)]})
    date = fields.datetime(
        'Date created', required=True, readonly=True,
        default=lambda self: fields.Datetime.now(),
        states={'draft': [('readonly', False)]}, )
    state = fields.Selection(
        STATE_SELECTION, 'State', readonly=True, select=True, default='draft',
        help="""
        The state of the move. A move that is still under planning is in a
        'Draft' state. Then the move goes to 'Reserved' state in order to
        reserve the designated amount. This move goes to 'Compromised' state
        when the purchase operation is confirmed. Finally goes to the
        'Executed' state where the amount is finally discounted from the budget
        available amount""")
    company_id = fields.Many2one('res.company', 'Company', required=True)
    fixed_amount = fields.Float(
        'Fixed amount', digits=dp.get_precision('Account'))
    standalone_move = fields.Boolean(
        'Standalone move', readonly=True, default=_check_manual,
        states={'draft': [('readonly', False)]})
    arch_reserved = fields.Float(
        'Original Reserved', digits=dp.get_precision('Account'))
    reserved = fields.Float(
        compute='_calc_reserved', string='Reserved', store=True)
    reversed = fields.Float(
        compute='_calc_reversed', string='Reversed', store=True)
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
        related='move_lines.budget_move_line_dist',
        string='Account Move Line Distribution')
    type = fields.Selection(
        selection='_select_types', string='Move Type', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    previous_move_id = fields.Many2one('budget.move', 'Previous move')
    from_migration = fields.Boolean('Created from migration')

    _defaults = {
        'company_id': lambda self: self.env'res.users').browse(cr, uid, uid, c).company_id.id,
    }


    @api.one
    def distribution_get(self, cr, uid, ids, *args):
        amld_obj = self.pool.get('account.move.line.distribution')
        result = []
        search_ids = []
        for move in self.browse(cr, uid, ids):
            for bud_move_line in move.move_lines:

                search_ids = amld_obj.search(cr, uid, [('target_budget_move_line_id','=', bud_move_line.id)])
            result = result + search_ids
        return result

 
    def _compute_executed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids,context=context):
            total=0.0
            for line in move.move_lines:
                total += line.executed 
            res[move.id]= total 
        return res
    
    def _compute_compromised(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids,context=context):
            total=0.0
            for line in move.move_lines:
                total += line.compromised 
            res[move.id]= total 
        return res
    
    def _check_non_zero(self, cr, uid, ids, context=None):
        for obj_bm in  self.browse(cr, uid, ids, context=context):
            if (obj_bm.fixed_amount == 0.0 or obj_bm.fixed_amount == None) and obj_bm.standalone_move == True and obj_bm.state in ('draft','reserved'):
                return False
        return True
    
    def _calc_reserved(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for bud_move in self.browse(cr, uid, ids, context=context):
            res_amount = 0
            if bud_move.state == 'reserved':       
                for line in bud_move.move_lines:
                    res_amount += line.reserved
            else:
                res_amount = 0
            res[bud_move.id] = res_amount
        return res
    
    def _calc_reversed(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for bud_move in self.browse(cr, uid, ids, context=context):
            res_amount = 0    
            for line in bud_move.move_lines:
                res_amount += line.reversed
            res[bud_move.id] = res_amount
        return res
    
    def recalculate_values(self, cr, uid, ids, context=None):
        mov_line_obj = self.pool.get('budget.move.line')
        for move in self.browse(cr, uid, ids, context=context):
            move_fixed_total = 0.0
            for line in move.move_lines:
                mov_line_obj.write(cr, uid, [line.id], {'date' : line.date}, context=context)
                move_fixed_total += line.fixed_amount
            self.write(cr, uid, ids, {'date': move.date, 'fixed_amount': move_fixed_total}, context=context) 
    
    def _select_types(self,cr,uid,context=None):
        #In case that the move is created from the view "view_budget_move_manual_form", modifies the selectable types
        #reducing them to modification, extension and opening
        if context == None:
            context={}
        if context.get('standalone_move',False):
            return [('modification',_('Modification')),
                ('extension',_('Extension')),
                ('opening',_('Opening')),
                ]
        
        else:
            return [
                ('invoice_in',_('Purchase invoice')),
                ('invoice_out',_('Sale invoice')),
                ('manual_invoice_in',_('Manual purchase invoice')),
                ('manual_invoice_out',_('Manual sale invoice')),
                ('expense',_('Expense')),
                ('payroll',_('Payroll')),
                ('manual',_('From account move')),
                ('modification',_('Modification')),
                ('extension',_('Extension')),
                ('opening',_('Opening')),
                ]

    @api.one
    def _check_manual(self):
        return True if self.env.context.get('standalone_move', False)\
            else False

    def _get_budget_moves_from_dist(self, cr, uid, ids, context=None):
        if ids:
            dist_obj = self.pool.get('account.move.line.distribution')
            dists = dist_obj.browse(cr, uid, ids, context = context)
            budget_move_ids = []
            for dist in dists:
                if dist.target_budget_move_line_id and \
                    dist.target_budget_move_line_id.budget_move_id and \
                    dist.target_budget_move_line_id.budget_move_id.id not in budget_move_ids:
                    budget_move_ids.append(dist.target_budget_move_line_id.budget_move_id.id)
            return budget_move_ids
        return []
    
    def _get_budget_moves_from_lines(self, cr, uid, ids, context=None):
        if ids:
            lines_obj = self.pool.get('budget.move.line')
            lines = lines_obj.browse(cr, uid, ids, context = context)
            budget_move_ids = []
            for line in lines:
                if line.budget_move_id and line.budget_move_id.id not in budget_move_ids:
                    budget_move_ids.append(line.budget_move_id.id)
            return budget_move_ids
        return []
    
    # Store triggers for functional fields
    STORE = {
        'budget.move':                      (lambda self, cr, uid, ids, context={}: ids, [], 10),
        'account.move.line.distribution':   (_get_budget_moves_from_dist, [], 10),
        'budget.move.line':                 (_get_budget_moves_from_lines, [], 10),
    }
    

    def transfer_to_next_year(self, cr, uid, move_ids, plan_id, context=None):
        MOVE_RELATED_MODELS=['account.invoice',
                               'account.move',
                               'hr.expense.expense',
                               'hr.payslip',
                               'purchase.order',
                               ]
        obj_bud_line= self.pool.get('budget.move.line')
        obj_prog_line= self.pool.get('budget.program.line')
        for move in self.browse(cr, uid, move_ids, context=context):
            vals={
                  'origin':move.origin,
                  'company_id': move.company_id.id,
                  'fixed_amount':move.fixed_amount,
                  'standalone_move':move.standalone_move,
                  'arch_reserved':move.arch_reserved,
                  'arch_compromised':move.arch_compromised,
                  'type':move.type,
                  'previous_move_id':move.id,
                  'from_migration':True
                  }
            new_move_id = self.create(cr, uid, vals, context=context)
            for line in move.move_lines:
                if line.executed != line.fixed_amount:
                    prog_line_id=line.program_line_id.id
                    next_prog_line = obj_prog_line.get_next_year_line(cr, uid,  [prog_line_id], context=context)[prog_line_id]
                    if next_prog_line:
                        line_vals={
                                   'origin':line.origin,
                                   'budget_move_id':new_move_id,
                                   'program_line_id':next_prog_line,
                                   'date':line.date,
                                   'fixed_amount':line.fixed_amount,
                                   'line_available':line.line_available,
                                   'po_line_id': line.po_line_id.id,
                                   'so_line_id': line.so_line_id.id,
                                   'inv_line_id': line.inv_line_id.id,
                                   'expense_line_id': line.expense_line_id.id,
                                   'tax_line_id': line.tax_line_id.id,
                                   'payslip_line_id': line.payslip_line_id.id,
                                   'move_line_id': line.move_line_id.id,
                                   'account_move_id': line.account_move_id.id,
                                   'previous_move_line_id':line.id
                                   }
                        new_move_line_id = obj_bud_line.create(cr, uid, line_vals, context=context)
                        fields_to_blank ={
                                   'po_line_id': None,
                                   'so_line_id': None,
                                   'inv_line_id': None,
                                   'expense_line_id': None,
                                   'tax_line_id': None,
                                   'payslip_line_id': None,
                                   'move_line_id': None,
                                   'account_move_id': None,
                                   }
                        obj_bud_line.write(cr, uid, [line.id], fields_to_blank, context=context)
            self.replace_budget_move(cr, uid, move.id, new_move_id, MOVE_RELATED_MODELS,context=context )
    
            if move.state == 'compromised':
                self.signal_workflow(cr, uid, [new_move_id], 'button_reserve', context=context)
                self.signal_workflow(cr, uid, [new_move_id], 'button_compromise', context=context)
            if move.state == 'in_execution':
                self.signal_workflow(cr, uid, [new_move_id], 'button_execute', context=context)
            
    def replace_budget_move(self, cr, uid, old_id, new_id, models,context=None ):
        for model in models:
            obj=self.pool.get(model)
            search_result = obj.search(cr, uid, [('budget_move_id','=',old_id)], context=context)
            obj.write(cr, uid, search_result, {'budget_move_id': new_id})
    
    def process_for_close(self, cr, uid, closeable_move_ids, plan_id, context=None):
        for move in self.browse(cr, uid, closeable_move_ids, context=context):
            if move.state in ('draft', 'reserved'):
                self.signal_workflow(cr, uid, [move.id], 'button_cancel', context=context)
            if move.state in ('compromised', 'in_execution'):
                self.transfer_to_next_year(cr, uid, [move.id], plan_id, context=context)
                self.signal_workflow(cr, uid, [move.id], 'button_transfer', context=context)

    def _check_values(self, cr, uid, ids, context=None):
        list_line_ids_repeat = []
        for move in self.browse(cr, uid, ids, context=context):
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
                        return [False, _(
                            """The amount to substract from %s is greater
                            than the available""" % line.program_line_id.name)]
        return [True, '']

    def create(self, cr, uid, vals, context={}):
        bud_program_lines_obj = self.pool.get('budget.program.line')
        bud_program_lines = []
        if 'code' not in vals.keys():
            vals['code'] = self.pool.get('ir.sequence').get(
                cr, uid, 'budget.move')
        elif vals['code'] is None or vals['code'] == '':
            vals['code'] = self.pool.get('ir.sequence').get(
                cr, uid, 'budget.move')
        # Extract program_line_id from values
        # (move_lines is a budget move line list)
        for bud_line in vals.get('move_lines', []):
            # position 3 is a dictionary, extract program_line_id value
            program_line_id = bud_line[2]['program_line_id']
            bud_program_lines.append(program_line_id)
        for line in bud_program_lines_obj.browse(
                cr, uid, bud_program_lines, context=context):
            if line.program_id.plan_id.state in ('approved', 'closed'):
                raise osv.except_osv(_('Error!'), _(
                    """You cannot create a budget move that have associated
                budget move lines with a approved or closed budget plan"""))

        res = super(budget_move, self).create(cr, uid, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        super(budget_move,self).write(cr, uid, ids, vals, context=context)
        for bud_move in self.browse(cr, uid, ids, context=context):
            if bud_move.state in ('reserved','draft') and bud_move.standalone_move :       
                res_amount=0
                for line in bud_move.move_lines:
                    res_amount += line.fixed_amount
                vals['fixed_amount'] = res_amount
                return super(budget_move,self).write(cr, uid, ids, {'fixed_amount':res_amount}, context=context)
        
    def on_change_move_line(self, cr, uid, ids, move_lines, context=None):
        res={}
        res_amount=0.0
        for move in self.browse(cr, uid, ids, context=context):
            if move.standalone_move:
                res_amount=0.0
                for line in move.move_lines:
                        res_amount += line.fixed_amount
        return {'value':{ 'fixed_amount':res_amount }}
            
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def action_reserve(self, cr, uid, ids, context=None):
        result = self._check_values(cr, uid, ids, context)#check positive or negative for different types of moves
        obj_mov_line = self.pool.get('budget.move.line')
        if result[0]:
            self.write(cr, uid, ids, {'state': 'reserved'})
            self.recalculate_values(cr, uid, ids, context=context)
        else:
            raise osv.except_osv(_('Error!'), result[1])
        return True
            
    def action_compromise(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid,ids, context=context):
            self.write(cr, uid, ids, {'state': 'compromised'})
            self.recalculate_values(cr, uid, ids, context=context)
            self.write(cr, uid, ids, {'arch_compromised': move.compromised, })
        return True
    
    def action_in_execution(self, cr, uid, ids, context=None):
        result = self._check_values(cr, uid, ids, context)
        if result[0]:
            self.write(cr, uid, ids, {'state': 'in_execution'})
            self.recalculate_values(cr, uid, ids, context=context)
        else:
            raise osv.except_osv(_('Error!'), result[1])
        return True
    
    def action_execute(self, cr, uid, ids, context=None):
        obj_mov_line = self.pool.get('budget.move.line')
        for move in self.browse(cr, uid,ids, context=context):
            self.write(cr, uid, [move.id], {'state': 'executed'})
            for line in move.move_lines:
                self.recalculate_values(cr, uid, ids, context=context)
            self.write(cr, uid, [move.id], {'state': 'executed'})
        return True
            
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.recalculate_values(cr, uid, ids, context=context)
        return True
    
    def action_transfer(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'transferred'})
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []    
        if not len(ids):
            return res
            
        for r in self.read(cr, uid, ids, ['code'], context):
            rec_name = '%s' % (r['code']) 
            res.append( (r['id'],rec_name) )
        return res
    
    def is_executed(self, cr, uid, ids, *args):
        dist_obj = self.pool.get('account.move.line.distribution') 
        executed = 0.0
        void = 0.0
        for move in self.browse(cr, uid, ids,):
            if move.type in ('opening','extension','modification'):
                if move.state == 'in_execution':
                    return True
            if move.type in ('manual_invoice_in','expense','invoice_in', 'payroll', 'manual'):
                distr_line_ids = []
                for line in move.move_lines:
                    distr_line_ids += dist_obj.search(cr, uid,[('target_budget_move_line_id','=',line.id)])
                for dist in dist_obj.browse(cr, uid, distr_line_ids):
                    if dist.account_move_line_type =='liquid':
                        executed += dist.distribution_amount
                    elif dist.account_move_line_type =='void':
                        void += dist.distribution_amount
                        
                if executed == move.fixed_amount - void:
                    return True
        return False
    
    def is_in_execution(self, cr, uid, ids, *args):
        dist_obj = self.pool.get('account.move.line.distribution') 
        executed = 0.0
        void = 0.0
        for move in self.browse(cr, uid, ids,):
            if move.type in ('opening','extension','modification'):
                    return False
            if move.type in ('manual_invoice_in','expense','invoice_in', 'payroll', 'manual'):
                distr_line_ids = []
                for line in move.move_lines:
                    distr_line_ids += dist_obj.search(cr, uid,[('target_budget_move_line_id','=',line.id)])
                for dist in dist_obj.browse(cr, uid, distr_line_ids):
                    if dist.account_move_line_type =='liquid':
                        executed += dist.distribution_amount
                    elif dist.account_move_line_type =='void':
                        void += dist.distribution_amount
                        
                if executed != move.fixed_amount - void:
                    return True
        return False
    
    def dummy_button(self,cr,uid, ids,context=None):
        return True   
    
    def unlink(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'draft':
                raise osv.except_osv(_('Error!'), _('Orders in state other than draft cannot be deleted \n'))
            for line in move.move_lines:
                if line.program_line_id.program_id.plan_id.state in ('approved','closed'):
                    raise osv.except_osv(_('Error!'), _('You cannot delete a budget move budget move that have associated budget lines with a approved or closed budget plan'))
           
        super(budget_move,self).unlink(cr, uid, ids, context=context)
