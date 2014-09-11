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
import openerp.addons.decimal_precision as dp

class accountWithholdingtax(orm.Model):
    _name = "account.withholding.tax"
    _description = "Account Withholding Tax"

    _columns = {
        'name': fields.char('Name', size=128),
        'code': fields.char('Code', size=64),
        'type': fields.selection([('percentage', 'Percent'),
                                   ('numeric', 'Numeric')], 'Withholding Tax Type',
                                   help="""Select here the kind of withholding tax. If you select percentage, you can't exceed 100%"""),

       'amount': fields.float('Amount/Percentage', digits_compute=dp.get_precision('Account')),
       'journal_id': fields.many2one('account.journal', 'Journal'),
    }
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Unfortunately this name is already used, please choose a unique one'),       
        ('code_unique', 'UNIQUE(code)', 'Unfortunately this code is already used, please choose a unique one')
    ]
            
    #Check amount 
    def _check_amount(self, cr, uid, ids, context=None):
        withholding_obj = self.browse(cr, uid, ids[0], context=context)
        
        #percentage over 100%
        if withholding_obj.type == 'percentage' and withholding_obj.amount > 100:
            return False
        
        #negative number
        if withholding_obj.amount < 0:
            return False        
        
        return True 
  
    #Journal must have default_debit_account and default_credit_account.
    def _check_debit_credit_accounts(self, cr, uid, ids, context=None):
        withholding_obj = self.browse(cr, uid, ids[0], context=context)
        
        if not withholding_obj.journal_id.default_credit_account_id and  not withholding_obj.journal_id.default_debit_account_id:
            return False
        return True    

    _constraints = [
            (_check_amount, 'Error!\nThe amount are invalid. Negative numbers and percentage over 100 are not allowed.', ['amount']),
            (_check_debit_credit_accounts, 'Error!\n The journal select must have default debit and default credit account', ['journal_id']),
    ]
    