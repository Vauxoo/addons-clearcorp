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
from openerp.osv import fields, osv, orm

class accountMove(orm.Model):
    _inherit = "account.move"
    
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))

        obj_sequence = self.pool.get('ir.sequence')
        
        #=============================================================================#
        check_lines = []
        next_step = False
        amount = 0.0
        percentage = 0.0
        obj_move_line = self.pool.get('account.move.line')
        
        #Check if this account.move has distributions lines and check (only in valid_moves -> is a account.move object)
        for move in self.browse(cr, uid, valid_moves, context=context):
            move_lines = obj_move_line.search(cr, uid, [('move_id','=',move.id)])
            
            for line in obj_move_line.browse(cr, uid, move_lines):
                if line.account_id.moves_cash:
                     check_lines.append(line)
        
            #Check amount in line.distribution (if there exist any line.id)
            if len(check_lines) > 0:
                for line in check_lines: 
                    distribution_lines = self.pool.get('account.move.line.distribution').search(cr, uid, [('account_move_line_id', '=', line.id)])
                    
                    if len(distribution_lines) > 0:
                        #Sum distribution_amount. This amount is equal to line.amount (debit or credit).
                        for distribution in self.pool.get('account.move.line.distribution').browse(cr, uid, distribution_lines):
                            amount += distribution.distribution_amount
                            percentage += distribution.distribution_percentage
                        
                        #Find amount (debit or credit) and compare. 
                        if line.debit > 0:
                            amount_check = line.debit
                        else:
                            amount_check = line.credit
                        
                        #Continue with normal process
                        if (amount_check == amount) and (percentage == 100):                        
                            next_step = True
                            
                        else:
                            next_step = False
                            return {'value': {'account_move_line_id': line.id},
                                    'warning':{'title':'Warning','message':'Distribution amount for this move line does not match with original amount line'}}
    
                    #Continue with normal process
                    else:
                        next_step = True
            
            else:
                next_step = True
            
            #=============================================================================#
            if next_step:
                for move in self.browse(cr, uid, valid_moves, context=context):
                    if move.name =='/':
                        new_name = False
                        journal = move.journal_id
        
                        if invoice and invoice.internal_number:
                            new_name = invoice.internal_number
                        else:
                            if journal.sequence_id:
                                c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                                new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                            else:
                                raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
                        
                        if new_name:
                            self.write(cr, uid, [move.id], {'name':new_name})
        
                cr.execute('UPDATE account_move '\
                           'SET state=%s '\
                           'WHERE id IN %s',
                           ('posted', tuple(valid_moves),))
        return True
