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

class Voucher(osv.Model):

    _inherit = 'account.voucher'

    # Get move lines for withholding taxes
    def _compute_withholding_move_lines(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for move in voucher.withholding_move_ids:
                move_ids.append(move.id)
            move_line_ids = self.pool.get('account.move.line').search(
                cr, uid, [('move_id','in',move_ids)])
            res[voucher.id] = move_line_ids
        return res

    # Get reverse move lines for withholding taxes
    def _compute_reverse_withholding_move_lines(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for move in voucher.withholding_move_ids:
                if move.move_reverse_id:
                    move_ids.append(move.move_reverse_id.id)
            move_line_ids = self.pool.get('account.move.line').search(
                cr, uid, [('move_id','in',move_ids)])
            res[voucher.id] = move_line_ids
        return res

    #Create a method that set the withholding tax from journal to voucher.
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id,
        partner_id, date, amount, ttype, company_id, context=None):

        vals = super(Voucher, self).onchange_journal(cr, uid, ids, journal_id,
            line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
        if not vals:
            vals = {}
        if journal_id:
            journal_obj = self.pool.get('account.journal').browse(
                cr, uid, journal_id, context)
            # Check if the journal has withholding taxes
            if journal_obj.withholding_tax_ids:
                if 'warning' in vals:
                    vals['warning'] = {
                        'title': 'Warning',
                        'message': 'The journal selected has withholding taxes assigned. '
                    'Please compute the taxes before validating the voucher.'
                    }
                else:
                    vals['warning'] = {
                        'title': 'Warning',
                        'message': 'The journal selected has withholding taxes assigned. '
                    'Please compute the taxes before validating the voucher.'
                    }
        return vals

    def _check_duplicate_withholding_taxes(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            tax_ids = []
            for tax in voucher.withholding_tax_lines:
                if tax.withholding_tax_id.id not in tax_ids:
                    tax_ids.append(tax.withholding_tax_id.id)
                else:
                    return False
        return True

    def compute_withholding_taxes(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            withholding_tax_lines = []
            for tax in voucher.journal_id.withholding_tax_ids:
                amount_to_pay = 0.0
                if tax.type == 'percentage':
                    amount_to_pay += (voucher.amount * tax.amount) / 100.0
                else:
                    amount_to_pay += tax.amount
                withholding_tax_lines.append((0,0,{
                    'amount': amount_to_pay,
                    'withholding_tax_id': tax.id,
                }))
            tax_ids = [tax.id for tax in voucher.withholding_tax_lines]
            self.pool.get('account.withholding.tax.line').unlink(
                cr, uid, tax_ids, context=context)
            if withholding_tax_lines:
                voucher.write({
                    'withholding_tax_lines': withholding_tax_lines
                })
        return True

    _columns = {
        'withholding_tax_lines': fields.one2many('account.withholding.tax.line',
            'voucher_id', string='Withholding Taxes', ondelete='cascade'),
        'withholding_move_ids':fields.one2many('account.move',
            'withholding_voucher_id', 'Withholding Moves'),
        'withholding_move_line_ids':fields.function(_compute_withholding_move_lines,
            string='Withholding Taxes', type='one2many',
            relation='account.move.line'),
        'withholding_move_line_ids_reverse':fields.function(
            _compute_reverse_withholding_move_lines, string='Reverse Withholding Taxes',
            type='one2many', relation='account.move.line'),
     }

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'withholding_move_ids': False,
        })
        return super(Voucher, self).copy(cr, uid, id, default, context=context)

    _constraints = [
        (_check_duplicate_withholding_taxes,'Withholding taxes can not be duplicated.',
         ['withholding_tax_lines']),
    ]

    #Method that create the move and move lines from withholding tax
    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(Voucher, self).action_move_line_create(cr, uid, ids, context)
        move_obj = self.pool.get('account.move')
        currency_obj = self.pool.get('res.currency')
        for voucher in self.browse(cr, uid, ids, context=context):
            # Currency of voucher and company
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)

            for tax in voucher.withholding_tax_lines:
                # Create the withholding move
                move_name = voucher.move_id.ref + ' ' + tax.withholding_tax_id.code 
                move_dict = self.account_move_get(cr, uid, voucher.id, context=context)
                move_dict['name'] = '/'
                move_dict['journal_id'] = tax.withholding_tax_id.journal_id.id
                move_dict['ref'] = move_name
                move_dict['narration'] = move_name
                move_dict['withholding_voucher_id'] =  voucher.id
                move_id = move_obj.create(cr, uid, move_dict, context=context)

                amount_currency = 0.0
                amount = 0.0
                """ Code found in account_voucher.py check if it is necessary to compute a 
                special currency
                date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
                ctx = context.copy()
                ctx.update({'date': date})
                voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
                voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
                ctx.update({
                    'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
                    'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})"""
                if company_currency <> current_currency:
                    amount = currency_obj.compute(cr, uid, current_currency,
                        company_currency, tax.amount, context=context)
                    amount_currency = tax.amount
                else:
                    amount = tax.amount
                # Get accounts based on the voucher type
                if voucher.type in ('purchase', 'payment'):
                    account_debit = voucher.account_id
                    account_credit = tax.withholding_tax_id.journal_id.default_credit_account_id
                elif voucher.type in ('sale', 'receipt'):
                    account_debit = tax.withholding_tax_id.journal_id.default_debit_account_id
                    account_credit = voucher.account_id

                line_name = voucher.move_id.ref + ' ' + tax.withholding_tax_id.code
                # Create the move lines for each tax
                move_line_debit = {
                    'name': line_name,
                    'debit': amount,
                    'credit': 0.0,
                    'account_id': account_debit.id,
                    'move_id': move_id,
                    'journal_id': tax.withholding_tax_id.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': amount_currency,
                    'date': voucher.date,
                    'date_maturity': voucher.date_due
                }
                
                move_line_credit = {
                    'name': line_name,
                    'debit': 0.0,
                    'credit': amount,
                    'account_id': account_credit.id,
                    'move_id': move_id,
                    'journal_id': tax.withholding_tax_id.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'partner_id': voucher.partner_id.id,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': -1.0 * amount_currency,
                    'date': voucher.date,
                    'date_maturity': voucher.date_due
                }
                self.pool.get('account.move.line').create(cr, uid, move_line_credit, context)
                self.pool.get('account.move.line').create(cr, uid, move_line_debit, context)
        return res

    def reverse_voucher(self, cr, uid, ids, context=None):
        res = super(Voucher, self).reverse_voucher(cr, uid, ids, context)
        
        for voucher in self.browse(cr, uid, ids, context=context):
            for withholding_move in voucher.withholding_move_ids:
                self.pool.get('account.move').reverse(cr, uid, [withholding_move.id], context=context)
        return res
