# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import errno
from openerp.osv import osv, fields
from openerp.tools.translate import _
import base64
import logging


class cash_budget_program_populate(osv.osv_memory):
    _name = 'cash.budget.program.populate'
    
    _columns = {
        'parent_account': fields.many2one('cash.budget.account', 'Catalog parent', domain=[('account_type','!=','budget'), ('active','=','True')], required=True),
        
    }

    def create_prog_line(self, cr, uid, program_id, program_code, parent_account_id=None, parent_line_id=None, previous_program_id=None,context=None ):
        prog_obj = self.pool.get('cash.budget.program')
        line_obj = self.pool.get('cash.budget.program.line')
        account_obj = self.pool.get('cash.budget.account')
        for account in account_obj.browse(cr, uid, [parent_account_id], context=context):
#            for child in account_obj.browse(cr, uid, account.child_parent_ids, context=context):
            if account.child_parent_ids:
                for child in account.child_parent_ids:
                    line_name = program_code + ' - [' + child.code + ']-' + child.name
                    previous_program_lines = line_obj.search(cr, uid, [('program_id','=',previous_program_id),('account_id','=',child.id),],context=context)
                    vals = {'parent_id':parent_line_id, 'account_id':child.id, 'program_id':program_id, 'name':line_name}
                    if previous_program_lines:
                        vals['previous_year_line_id'] = previous_program_lines[0]
                    new_line = line_obj.create(cr, uid, vals,context=context )
                    program = prog_obj.browse(cr,uid,[program_id],context=context)[0]
                    self.create_prog_line(cr, uid, program_id, program_code, child.id, new_line, previous_program_id=program.previous_program_id.id, context=context )
            if account.child_consol_ids:
                program = prog_obj.browse(cr,uid,[program_id],context=context)[0]
                parent_line = line_obj.browse(cr, uid, [parent_line_id],context=context)[0]
                for consol_child in account.child_consol_ids:
                    prog_lines=line_obj.search(cr, uid, [('account_id','=',consol_child.id)],context=context)
                    for prg_line in line_obj.browse(cr,uid,prog_lines,context=context):
                          if program.plan_id.id == prg_line.program_id.plan_id.id:
                              line_obj.write(cr,uid,[parent_line.id],{'child_consol_ids':[(4,prg_line.id)]}) 
                    #line_name = program_code + ' - [' + child.code + ']-' + child.name
                    #new_line = line_obj.create(cr, uid, {'parent_id':parent_line_id, 'account_id':child.id, 'program_id':program_id, 'name':line_name} )
                    #self.create_prog_line(cr, uid, program_id, program_code, child.id, new_line, context=context)
        return True
    
    def bulk_line_create(self, cr, uid, ids, context=None):
        prog_obj = self.pool.get('cash.budget.program')
        line_obj = self.pool.get('cash.budget.program.line')
        account_obj = self.pool.get('cash.budget.account')
        data = self.browse(cr, uid, ids, context=context)[0]
        for program in prog_obj.browse(cr, uid, context['active_ids'], context=context):
            current_lines = len(program.program_lines)
            if current_lines > 0:
                raise osv.except_osv(_('Error!'), _('This program already contains program lines'))
            line_name = program.code + ' - [' + data.parent_account.code + ']-' + data.parent_account.name
            new_line = line_obj.create(cr, uid, {'account_id':data.parent_account.id, 'program_id':program.id, 'name':line_name} )
            self.create_prog_line(cr, uid, program.id, program.code, data.parent_account.id, new_line , previous_program_id=program.previous_program_id.id, context=context)
        return True
            
            
        
    
