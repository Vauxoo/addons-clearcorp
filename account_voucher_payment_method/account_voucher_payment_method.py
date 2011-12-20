# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Frank Carvajal. Copyright ClearCorp SA
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

from osv import osv, fields
from tools import debug

class account_journal(osv.osv):
	_name = "account.journal"
	_inherit = "account.journal"
	_columns = {
		#'type': fields.selection([('sale', 'Sale'),
		#						('sale_refund','Sale Refund'), 
		#						('purchase', 'Purchase'), 
		#						('purchase_refund','Purchase Refund'), 
		#						('cash', 'Cash'), 
		#						('bank', 'Bank and Cheques'), 
		#						('general', 'General'), 
		#						('situation', 'Opening/Closing Situation'),
		#						('payment','Payment method')], 'Type', size=32, required=True,
		#						help="Select 'Sale' for Sale journal to be used at the time of making invoice."\
		#						" Select 'Purchase' for Purchase Journal to be used at the time of approving purchase order."\
		#						" Select 'Cash' to be used at the time of making payment."\
		#						" Select 'General' for miscellaneous operations."\
		#						" Select 'Opening/Closing Situation' to be used at the time of new fiscal year creation or end of year entries generation."),
		'payment_method'            : fields.boolean('Payment method'),
		'payment_verification'      : fields.boolean('Payment Verification'),
	}
account_journal()

class account_voucher_journal_payment(osv.osv):
	_name = 'account.voucher'
	_inherit = 'account.voucher'
	_description = 'Accounting Voucher'
	
	def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
		"""price
		Returns a dict that contains new values and context

		@param partner_id: latest value from user input for field partner_id
		@param args: other arguments
		@param context: context arguments, like lang, time zone

		@return: Returns a dict which contains new values, and context
		"""
		if context is None:
			context = {}
		if not journal_id:
			return {}
		context_multi_currency = context.copy()
		if date:
			context_multi_currency.update({'date': date})

		line_pool = self.pool.get('account.voucher.line')
		line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
		if line_ids:
			line_pool.unlink(cr, uid, line_ids)

		currency_pool = self.pool.get('res.currency')
		move_line_pool = self.pool.get('account.move.line')
		partner_pool = self.pool.get('res.partner')
		journal_pool = self.pool.get('account.journal')

		vals = self.onchange_journal(cr, uid, ids, journal_id, [], False, partner_id, context)
		vals = vals.get('value')
		currency_id = vals.get('currency_id', currency_id)
		default = {
			'value':{'line_ids':[], 'line_dr_ids':[], 'line_cr_ids':[], 'pre_line': False, 'currency_id':currency_id},
		}

		if not partner_id:
			return default

		if not partner_id and ids:
			line_ids = line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
			if line_ids:
				line_pool.unlink(cr, uid, line_ids)
			return default

		journal = journal_pool.browse(cr, uid, journal_id, context=context)
		partner = partner_pool.browse(cr, uid, partner_id, context=context)
		account_id = False
		if journal.type in ('sale','sale_refund'):
			account_id = partner.property_account_receivable.id
		elif journal.type in ('purchase', 'purchase_refund','expense'):
			account_id = partner.property_account_payable.id
		else:
			account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

		default['value']['account_id'] = account_id

		if journal.type not in ('cash', 'bank','payment'):
			return default

		total_credit = 0.0
		total_debit = 0.0
		account_type = 'receivable'
		if ttype == 'payment':
			account_type = 'payable'
			total_debit = price or 0.0
		else:
			total_credit = price or 0.0
			account_type = 'receivable'

		if not context.get('move_line_ids', False):
			domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
			if context.get('invoice_id', False):
				domain.append(('invoice', '=', context['invoice_id']))
			ids = move_line_pool.search(cr, uid, domain, context=context)
		else:
			ids = context['move_line_ids']
		ids.reverse()
		moves = move_line_pool.browse(cr, uid, ids, context=context)

		company_currency = journal.company_id.currency_id.id
		if company_currency != currency_id and ttype == 'payment':
			total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
		elif company_currency != currency_id and ttype == 'receipt':
			total_credit = currency_pool.compute(cr, uid, currency_id, company_currency, total_credit, context=context_multi_currency)

		for line in moves:
			if line.credit and line.reconcile_partial_id and ttype == 'receipt':
				continue
			if line.debit and line.reconcile_partial_id and ttype == 'payment':
				continue
			total_credit += line.credit or 0.0
			total_debit += line.debit or 0.0
		for line in moves:
			if line.credit and line.reconcile_partial_id and ttype == 'receipt':
				continue
			if line.debit and line.reconcile_partial_id and ttype == 'payment':
				continue
			original_amount = line.credit or line.debit or 0.0
			amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
			rs = {
				'name':line.move_id.name,
				'type': line.credit and 'dr' or 'cr',
				'move_line_id':line.id,
				'account_id':line.account_id.id,
				'amount_original': currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency) or original_amount, context=context_multi_currency),
				'date_original':line.date,
				'date_due':line.date_maturity,
				'amount_unreconciled': amount_unreconciled,
			}

			if line.credit:
				amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(total_debit), context=context_multi_currency))
				rs['amount'] = amount
				total_debit -= amount
			else:
				amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(total_credit), context=context_multi_currency))
				rs['amount'] = amount
				total_credit -= amount

			default['value']['line_ids'].append(rs)
			if rs['type'] == 'cr':
				default['value']['line_cr_ids'].append(rs)
			else:
				default['value']['line_dr_ids'].append(rs)

			if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
				default['value']['pre_line'] = 1
			elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
				default['value']['pre_line'] = 1
			default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)

		return default
	
	def proforma_voucher_mirror(self, cr, uid, ids, context=None):
		debug("USING OVERRIDE METHOD")
		super(account_voucher_journal_payment, self).action_move_line_create(cr, uid, ids, context=context)
		voucher = self.browse(cr,uid,ids,context=context)[0]
		if voucher.journal_id.journal_mirror:
			mirror_journal = voucher.journal_id.journal_mirror
			targ_journal =  mirror_journal.targ_journal
			targ_account = mirror_journal.targ_account
			company_id = self.pool.get('res.company').browse(cr,uid,1)
			partner_id = company_id.partner_id
			
			args = {
				'journal' : targ_journal,
				'account' : targ_account,
				'partner' : partner_id,
			}
			debug(args)
			self.action_move_line_create_mirror(cr,uid,ids,args,context=context)
		return True    
	
	def action_move_line_create_mirror(self, cr, uid, ids,args, context=None):
		def _get_payment_term_lines(term_id, amount):
			term_pool = self.pool.get('account.payment.term')
			if term_id and amount:
				terms = term_pool.compute(cr, uid, term_id, amount)
				return terms
			return False
		if context is None:
			context = {}
		move_pool = self.pool.get('account.move')
		move_line_pool = self.pool.get('account.move.line')
		currency_pool = self.pool.get('res.currency')
		tax_obj = self.pool.get('account.tax')
		seq_obj = self.pool.get('ir.sequence')
		
		debug(ids)
		for inv in self.browse(cr, uid, ids, context=context):
			debug("DENTRO DEL FOR")
			debug(inv)
			debug(inv.move_id)
			mirror_journal_id = args.get('journal',False)
			mirror_account_id = args.get('account',False)
			period_id = args.get('period',False)
			partner_id = args.get('partner',False)
			
			#if inv.move_id:
			#	continue
			context_multi_currency = context.copy()
			context_multi_currency.update({'date': inv.date})
			debug("CONTINUE")
			if inv.number:
				name = inv.number
			elif mirror_journal_id.sequence_id:
				name = seq_obj.get_id(cr, uid, mirror_journal_id.sequence_id.id)
			else:
				raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))
			if not inv.reference:
				ref = name.replace('/','')
			else:
				ref = inv.reference

			move = {
				'name': name,
				'journal_id': mirror_journal_id and mirror_journal_id.id or inv.journal_id.id,
				'narration': inv.narration,
				'date': inv.date,
				'ref': ref,
				'period_id': period_id and period_id.id or (inv.period_id and inv.period_id.id or False)
			}
			move_id = move_pool.create(cr, uid, move)
			debug(move)
			#create the first line manually
			company_currency = mirror_journal_id and mirror_journal_id.company_id.currency_id.id or inv.journal_id.company_id.currency_id.id
			current_currency = mirror_journal_id and mirror_journal_id.currency_id.id or inv.currency_id.id
			
			debug(company_currency)
			debit = 0.0
			credit = 0.0
			# TODO: is there any other alternative then the voucher type ??
			# -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
			if inv.type in ('purchase', 'payment'):
				credit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
			elif inv.type in ('sale', 'receipt'):
				debit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
			if debit < 0:
				credit = -debit
				debit = 0.0
			if credit < 0:
				debit = -credit
				credit = 0.0
			sign = debit - credit < 0 and -1 or 1
			#create the first line of the voucher
			move_line = {
				'name': inv.name or '/',
				'debit': debit,
				'credit': credit,
				'account_id': mirror_account_id and mirror_account_id.id or inv.account_id.id,
				'move_id': move_id,
				'journal_id': mirror_journal_id and mirror_journal_id.id or inv.journal_id.id,
				'period_id': period_id and period_id.id or inv.period_id.id,
				'partner_id': partner_id and partner_id.id inv.partner_id.id,
				'currency_id': company_currency <> current_currency and  current_currency or False,
				'amount_currency': company_currency <> current_currency and sign * inv.amount or 0.0,
				'date': inv.date,
				'date_maturity': inv.date_due
			}
			debug(move_line)
			move_line_pool.create(cr, uid, move_line)
			rec_list_ids = []
			line_total = debit - credit
			if inv.type == 'sale':
				line_total = line_total - currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
			elif inv.type == 'purchase':
				line_total = line_total + currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)

			debug(inv.line_ids)
			for line in inv.line_ids:
				#create one move line per voucher line where amount is not 0.0
				if not line.amount:
					continue
				#we check if the voucher line is fully paid or not and create a move line to balance the payment and initial invoice if needed
				if line.amount == line.amount_unreconciled:
					amount = line.move_line_id.amount_residual #residual amount in company currency
				else:
					amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.untax_amount or line.amount, context=context_multi_currency)
				
				move_line = {
					'journal_id': mirror_journal_id and mirror_journal_id.id or inv.journal_id.id,
					'period_id': period_id and period_id.id or inv.period_id.id,
					'name': line.name and line.name or '/',
					'account_id': mirror_account_id and mirror_account_id.id or line.account_id.id,
					'move_id': move_id,
					'partner_id': partner_id and  partner_id.id or inv.partner_id.id,
					'currency_id': company_currency <> current_currency and current_currency or False,
					'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
					'quantity': 1,
					'credit': 0.0,
					'debit': 0.0,
					'date': inv.date
				}
				debug(move_line)
				if amount < 0:
					amount = -amount
					if line.type == 'dr':
						line.type = 'cr'
					else:
						line.type = 'dr'

				if (line.type=='dr'):
					line_total += amount
					move_line['debit'] = amount
				else:
					line_total -= amount
					move_line['credit'] = amount

				if inv.tax_id and inv.type in ('sale', 'purchase'):
					move_line.update({
						'account_tax_id': inv.tax_id.id,
					})
				if move_line.get('account_tax_id', False):
					tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
					if not (tax_data.base_code_id and tax_data.tax_code_id):
						raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))
				sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
				move_line['amount_currency'] = company_currency <> current_currency and sign * line.amount or 0.0
				voucher_line = move_line_pool.create(cr, uid, move_line)
				if line.move_line_id.id:
					rec_ids = [voucher_line, line.move_line_id.id]
					rec_list_ids.append(rec_ids)

			#VER QUE HACER CON LAS DE AJUSTE
			inv_currency_id = current_currency or mirror_journal_id.currency or mirror_journal_id.company_id.currency_id
			if not currency_pool.is_zero(cr, uid, inv_currency_id, line_total):
				diff = line_total
				account_id = False
				if inv.payment_option == 'with_writeoff':
					account_id = mirror_account_id and mirror_account_id.id or inv.writeoff_acc_id.id
				elif inv.type in ('sale', 'receipt'):
					account_id = mirror_account_id and mirror_account_id.id or (partner_id and partner_id.property_account_receivable.id or inv.partner_id.property_account_receivable.id)
				else:
					account_id = mirror_account_id and mirror_account_id.id or (partner_id and partner_id.property_account_payable.id or inv.partner_id.property_account_payable.id)
				move_line = {
					'name': name,
					'account_id': account_id,
					'move_id': move_id,
					'partner_id': partner_id and partner_id.id or inv.partner_id.id,
					'date': inv.date,
					'credit': diff > 0 and diff or 0.0,
					'debit': diff < 0 and -diff or 0.0,
					#'amount_currency': company_currency <> current_currency and currency_pool.compute(cr, uid, company_currency, current_currency, diff * -1, context=context_multi_currency) or 0.0,
					#'currency_id': company_currency <> current_currency and current_currency or False,
				}
				move_line_pool.create(cr, uid, move_line)
			#self.write(cr, uid, [inv.id], {
			#	'move_id': move_id,
			#	'state': 'posted',
			#	'number': name,
			#})
			move_pool.post(cr, uid, [move_id], context={})
			for rec_ids in rec_list_ids:
				if len(rec_ids) >= 2:
					move_line_pool.reconcile_partial(cr, uid, rec_ids)
		return True    
account_voucher_journal_payment()

class account_voucher_line(osv.osv):
	_name = 'account.voucher.line'
	_inherit = 'account.voucher.line'
	_columns = {
		'currency_id' :  fields.related('move_line_id', 'currency_id', type = 'many2one', relation = 'account.invoice', string = 'Currency', readonly=True,store=False),
	}
account_voucher_line()
