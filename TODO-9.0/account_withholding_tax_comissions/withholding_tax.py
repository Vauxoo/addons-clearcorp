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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class WithholdingTax(osv.Model):

    _name = 'account.withholding.tax'

    _description = 'Account Withholding Taxes'

    def _get_amount_in_company_currency(self, cr, uid, ids, context=None):
        return self.browse(cr, uid, ids[0], context=context).amount

    _columns = {
        'name': fields.char('Name', size=128),
        'code': fields.char('Code', size=64),
        'type': fields.selection([('percentage', 'Percent'),('numeric', 'Numeric')],
            'Withholding Tax Type', help='Select here the kind of withholding tax. If '
            'you select percentage, you can\'t exceed 100%'),
       'amount': fields.float('Amount/Percentage', digits_compute=dp.get_precision('Account')),
       'journal_id': fields.many2one('account.journal', 'Journal'),
    }

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The tax name must be unique'),
        ('code_unique', 'UNIQUE(code)', 'The tax code must be unique')
    ]

    def _check_amount(self, cr, uid, ids, context=None):
        for tax in self.browse(cr, uid, ids, context=context):
            # Check if it is percentage and amount is over 100
            if tax.type == 'percentage' and tax.amount > 100:
                return False
            # Check if it is a negative number
            if tax.amount < 0:
                return False
        return True

    def _check_debit_credit_accounts(self, cr, uid, ids, context=None):
        for tax in self.browse(cr, uid, ids, context=context):
            if not tax.journal_id.default_credit_account_id and \
            not tax.journal_id.default_debit_account_id:
                return False
        return True

    _constraints = [
            (_check_amount, 'The amount is invalid. Negative numbers and '
             'percentages over 100% are not allowed.', ['amount']),
            (_check_debit_credit_accounts, 'The journal selected must have '
             'default debit and default credit account', ['journal_id']),
    ]