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

from openerp.osv import osv

class BankStatement(osv.Model):
    
    _inherit = 'account.bank.statement'
    
    def button_confirm_bank(self, cr, uid, ids, context=None):
        res = super(BankStatement,self).button_confirm_bank(cr, uid, ids, context=context)
        for st in self.browse(cr, uid, ids, context=context):
            for move_line in st.move_line_ids:
                # Skip if move_line is reconciled. Legacy due to account_banking_ccorp
                if move_line.reconcile:
                    continue
                if not move_line.account_id.reconcile:
                    continue
                # Check if move line is debit
                if not move_line.debit == 0.0:
                    cr.execute('''SELECT
  line.id,
  line.ref,
  line.debit,
  line.credit,
  line.date
FROM
  (SELECT 
    line.id,
    line.ref,
    line.debit,
    line.credit,
    line.date
  FROM 
    account_move_line AS line
  WHERE 
    line.reconcile_id IS NULL AND
    line.reconcile_partial_id IS NULL AND
    line.company_id = %s AND
    line.period_id = %s AND
    line.account_id = %s AND
    line.state = 'valid' AND
    line.id != %s) AS line
WHERE
  line.ref = %s AND
  line.credit - %s = 0 AND
  line.debit = 0;''', (st.company_id.id, st.period_id.id, move_line.account_id.id,
                        move_line.id, move_line.ref or '', move_line.debit))
                # Move line is credit
                else:
                    cr.execute('''SELECT
  line.id,
  line.ref,
  line.debit,
  line.credit,
  line.date
FROM
  (SELECT 
    line.id,
    line.ref,
    line.debit,
    line.credit,
    line.date
  FROM 
    account_move_line AS line
  WHERE 
    line.reconcile_id IS NULL AND
    line.reconcile_partial_id IS NULL AND
    line.company_id = %s AND
    line.period_id = %s AND
    line.account_id = %s AND
    line.state = 'valid' AND
    line.id != %s) AS line
WHERE
  line.ref = %s AND
  line.debit - %s = 0 AND
  line.credit = 0;''', (st.company_id.id, st.period_id.id, move_line.account_id.id,
                       move_line.id, move_line.ref or '', move_line.credit))
                
                result = cr.dictfetchall()
                # Skip if there are more than one match
                if len(result) > 1:
                    continue
                # Try to look for results using dates if
                # no result was found
                elif len(result) == 0:
                    # Check again if move line is debit
                    if not move_line.debit == 0.0:
                        cr.execute('''SELECT
  line.id,
  line.ref,
  line.debit,
  line.credit,
  line.date
FROM
  (SELECT 
    line.id,
    line.ref,
    line.debit,
    line.credit,
    line.date
  FROM 
    account_move_line AS line
  WHERE 
    line.reconcile_id IS NULL AND
    line.reconcile_partial_id IS NULL AND
    line.company_id = %s AND
    line.period_id = %s AND
    line.account_id = %s AND
    line.state = 'valid' AND
    line.id != %s) AS line
WHERE
  (line.date + 1 = date %s OR
  line.date - 1 = date %s) AND
  line.credit - %s = 0 AND
  line.debit = 0;''', (st.company_id.id, st.period_id.id, move_line.account_id.id,
                        move_line.id, move_line.date, move_line.date, move_line.debit))
                    # Move line is credit
                    else:
                        cr.execute('''SELECT
  line.id,
  line.ref,
  line.debit,
  line.credit,
  line.date
FROM
  (SELECT 
    line.id,
    line.ref,
    line.debit,
    line.credit,
    line.date
  FROM 
    account_move_line AS line
  WHERE 
    line.reconcile_id IS NULL AND
    line.reconcile_partial_id IS NULL AND
    line.company_id = %s AND
    line.period_id = %s AND
    line.account_id = %s AND
    line.state = 'valid' AND
    line.id != %s) AS line
WHERE
  (line.date + 1 = date %s OR
  line.date - 1 = date %s) AND
  line.debit - %s = 0 AND
  line.credit = 0;''', (st.company_id.id, st.period_id.id, move_line.account_id.id,
                       move_line.id, move_line.date, move_line.date, move_line.credit))
                    
                    result = cr.dictfetchall()
                    
                    # Skip if there are more than one match. Or None at all
                    if len(result) > 1 or len(result) == 0:
                        continue
                
                # Do the full reconcile
                account_move_line_obj = self.pool.get('account.move.line')
                account_move_line_obj.reconcile(cr, uid, [move_line.id, result[0].get('id')], 'manual',
                    move_line.account_id.id, st.period_id.id, False, context=context)
        return res
                    
