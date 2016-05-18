# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from operator import itemgetter
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging
import openerp.netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, orm, osv

class budget_move_line(osv.osv):
    _name = "budget.move.line"
    _description = "Budget Move Line"
    
    def on_change_program_line(self, cr, uid, ids, program_line, context=None):
        for line in self.pool.get('budget.program.line').browse(cr, uid,[program_line], context=context):
            return {'value': {'line_available':line.available_budget},}
        return {'value': {}}
    
    def _compute(self, cr, uid, ids, field_names, args, context=None, ignore_dist_ids=[]):
        amld = self.pool.get('account.move.line.distribution')
        fields = ['compromised', 'executed','reversed', 'reserved']
        res = {}
        lines = self.browse(cr, uid, ids,context=context)
         
        for line in lines:
            res[line.id] = {}
            executed = 0.0
            compromised = 0.0
            reversed = 0.0
            reserved = 0.0
            if line.state in ('executed','in_execution','transferred'):
                if line.type == 'opening':
                    executed = line.fixed_amount
                    
                elif line.type in ('manual_invoice_in','expense','invoice_in','payroll','manual'):
                    line_ids_bar = amld.search(cr, uid, [('target_budget_move_line_id','=', line.id),('account_move_line_type','=','liquid')], context=context)
                    for bar_line in amld.browse(cr, uid, line_ids_bar, context=context):
                        if bar_line.id in ignore_dist_ids:
                            continue
                        executed += bar_line.distribution_amount
            
            void_line_ids_amld = amld.search(cr, uid, [('target_budget_move_line_id','=', line.id),('account_move_line_type','=','void')], context=context)
            for void_line in amld.browse(cr, uid, void_line_ids_amld, context=context):
                if void_line.id in ignore_dist_ids:
                    continue
                reversed += void_line
            
            if line.previous_move_line_id:
                executed = executed + line.previous_move_line_id.executed
                reversed = reversed + line.previous_move_line_id.reversed
                        
            if line.state in ('compromised','executed','in_execution','transferred'):
                compromised = line.fixed_amount - executed - line.reversed
            
            if line.state == 'reserved':
                    reserved = line.fixed_amount - reversed
                
            res[line.id]['executed'] = executed
            res[line.id]['compromised'] = compromised 
            res[line.id]['reversed'] = reversed
            res[line.id]['reserved'] = reserved 
        return res
    
    def compute(self, cr, uid, ids, field_names, args, context=None, ignore_dist_ids=[]):
        return self._compute(cr, uid, ids, field_names, args, context, ignore_dist_ids)

    def _compute_modified(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        lines = self.browse(cr, uid, ids,context=context) 
        for line in lines:
            total = 0.0
            if line.state == 'executed':
                if line.type == 'modification':
                    total = line.fixed_amount
            res[line.id]= total 
        return res
    
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
        lines = self.browse(cr, uid, ids,context=context) 
        for line in lines:
            name = str(line.budget_move_id.code) + "\\" + str(line.origin)
            res[line.id] = name 
        return res
    
    
    _columns = {
        'origin': fields.char('Origin', size=64, ),
        'budget_move_id': fields.many2one('budget.move', 'Budget Move', required=True, ondelete='cascade'),
        'name': fields.function(_line_name, type='char', method=True, string='Name',readonly=True, store=True),
        'code': fields.related('origin', type='char', size=64, string = 'Origin'),
        'program_line_id': fields.many2one('budget.program.line', 'Program line', required=True),
        'date': fields.datetime('Date created', required=True,),
        'fixed_amount': fields.float('Original amount',digits_compute=dp.get_precision('Account'),),
        'line_available':fields.float('Line available',digits_compute=dp.get_precision('Account'),readonly=True),
        'changed': fields.function(_compute_modified, type='float', method=True, string='Modified',readonly=True, store=True),
        'extended': fields.function(_compute_extended, type='float', method=True, string='Extended',readonly=True, store=True),
        'reserved': fields.function(_compute, type='float', method=True, multi=True, string='Reserved',readonly=True, store=True),
        'reversed': fields.function(_compute, type='float', method=True, multi=True, string='Reversed',readonly=True, store=True),
        'compromised': fields.function(_compute, type='float', method=True, multi=True, string='Compromised', readonly=True, store=True),
        'executed': fields.function(_compute, type='float', method=True, multi=True, string='Executed',readonly=True, store=True),
        'po_line_id': fields.many2one('purchase.order.line', 'Purchase order line', ),
        'so_line_id': fields.many2one('sale.order.line', 'Sale order line', ),
        'inv_line_id': fields.many2one('account.invoice.line', 'Invoice line', ),
        'expense_line_id': fields.many2one('hr.expense.line', 'Expense line', ),
        'tax_line_id': fields.many2one('account.invoice.tax', 'Invoice tax line', ),
        'payslip_line_id': fields.many2one('hr.payslip.line', 'Payslip line', ),
        'move_line_id': fields.many2one('account.move.line', 'Move line', ),
        'account_move_id': fields.many2one('account.move', 'Account Move', ),
        'type': fields.related('budget_move_id', 'type', type='char', relation='budget.move', string='Type', readonly=True),
        'state': fields.related('budget_move_id', 'state', type='char', relation='budget.move', string='State',  readonly=True),
        #=======bugdet move line distributions
        'budget_move_line_dist': fields.one2many('account.move.line.distribution','target_budget_move_line_id', 'Budget Move Line Distributions'),
        'type_distribution':fields.related('budget_move_line_dist','type', type="selection", relation="account.move.line.distribution", string="Distribution type", selection=[('manual', 'Manual'), ('auto', 'Automatic')]),
        #=======Payslip lines
        'previous_move_line_id': fields.many2one('budget.move', 'Previous move line'),
        'from_migration':fields.related('budget_move_id','from_migration', type="boolean", relation='budget.move', string='Transferred', readonly=True)

    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'reversed': 0.0,
        'from_migration':False
        }
    
    _constraints=[
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

    def unlink(self, cr, uid, ids, context=None):
        for bud_move_line in self.browse(cr, uid, ids, context=context):
             if bud_move_line.program_line_id.program_id.plan_id.state in ('cancel','closed'):
                raise osv.except_osv(_('Error!'), _('You cannot create a budget move with a canceled or closed plan'))
        super(budget_move_line, self).unlink(cr, uid, ids, context=context)
