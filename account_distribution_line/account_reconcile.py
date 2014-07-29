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

from osv import fields, osv, orm
#import decimal_precision as dp
from tools.translate import _
#from datetime import datetime
#from copy import copy

class AccountMoveReconcile(orm.Model):
    _inherit = 'account.move.reconcile'

    def check_incremental_reconcile(self, cr, uid, vals, context=None):
        #Checks for every account move line, that if the AML(account move line) has a reconcile (partial or complete), each AML of the given reconcile must be e included in the new reconcile.
        acc_move_line_obj=self.pool.get('account.move.line')
        acc_move_line_tuples=[]
        acc_move_line_ids=[]
        previous_reconciles = []
        
        if vals.get('line_id', False):
            acc_move_line_tuples=vals.get('line_id', False)
        if vals.get('line_partial_ids', False):
            acc_move_line_tuples=vals.get('line_partial_ids', False)

        for tuple in acc_move_line_tuples:
            if tuple[0]== 4:
                acc_move_line_ids.append(tuple[1])

        for acc_move_line in acc_move_line_obj.browse(cr, uid, acc_move_line_ids, context=context):
             previous_reconcile = acc_move_line.reconcile_id
             previous_partial_reconcile = acc_move_line.reconcile_partial_id
             
             if previous_reconcile:
                 for aml in previous_reconcile.line_id:
                     if aml.id not in acc_move_line_ids:
                         return False
             elif previous_partial_reconcile:
                 for aml in previous_partial_reconcile.line_partial_ids:
                     if aml.id not in acc_move_line_ids:
                         return False
        return True
    
    def split_debit_credit(self,cr, uid, move_line_ids,context=None):
        #takes a list of given account move lines and classifies them in credit or debit
        #returns a dictionary with two keys('debit' and 'credit') and for values lists of account move line ids
        result ={}
        credit = []
        debit = []
        acc_move_line = self.pool.get('account.move.line')
        for line in acc_move_line.browse(cr, uid, move_line_ids,context=context):
            if line.credit > 0:
                credit.append(line.id)
            elif line.debit > 0:
                debit.append(line.id)
            elif line.debit == 0 and line.credit == 0:
                if line.amount_currency > 0:
                    debit.append(line.id)
                else:
                    credit.append(line.id)
        result ['debit'] = debit
        result ['credit'] = credit
        return result
    
    def _get_reconcile_counterparts(self, cr, uid, line, context={}):
        is_debit = True if line.debit else False
        reconcile_ids = []
        
        if line.reconcile_id:
            reconcile_lines = line.reconcile_id.line_id if line.reconcile_id and line.reconcile_id.line_id else []
            reconcile_ids.append(line.reconcile_id.id)
        elif line.reconcile_partial_id:
            reconcile_lines = line.reconcile_partial_id.line_partial_ids if line.reconcile_partial_id and line.reconcile_partial_id.line_partial_ids else []
            reconcile_ids.append(line.reconcile_partial_id.id)
        else:
            reconcile_lines = []
        
        res = []
        if reconcile_lines:
            for move_line in reconcile_lines:
                if (is_debit and move_line.credit) or (not is_debit and move_line.debit):
                    res.append(move_line)
        return reconcile_ids, res