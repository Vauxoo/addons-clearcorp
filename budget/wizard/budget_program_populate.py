# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import errno
from osv import osv, fields
from tools.translate import _
import base64
import logging


class budget_program_populate(osv.osv_memory):
    _name = 'budget.program.populate'
    
    _columns = {
        'parent_account': fields.many2one('budget.account', 'Catalog parent', domain=[('account_type','!=','budget'), ('active','=','True')]),
        
    }

    def create_prog_line(self, cr, uid, program_id, program_code, parent_account_id=None, parent_line_id=None, previous_program_id=None,context=None ):
        prog_obj = self.pool.get('budget.program')
        line_obj = self.pool.get('budget.program.line')
        account_obj = self.pool.get('budget.account')
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
        prog_obj = self.pool.get('budget.program')
        line_obj = self.pool.get('budget.program.line')
        account_obj = self.pool.get('budget.account')
        data = self.browse(cr, uid, ids, context=context)[0]
        for program in prog_obj.browse(cr, uid, context['active_ids'], context=context):
            current_lines = len(program.program_lines)
            if current_lines > 0:
                raise osv.except_osv(_('Error!'), _('This program already contains program lines'))
            line_name = program.code + ' - [' + data.parent_account.code + ']-' + data.parent_account.name
            new_line = line_obj.create(cr, uid, {'account_id':data.parent_account.id, 'program_id':program.id, 'name':line_name} )
            self.create_prog_line(cr, uid, program.id, program.code, data.parent_account.id, new_line , previous_program_id=program.previous_program_id.id, context=context)
        return True
            
            
        
    
