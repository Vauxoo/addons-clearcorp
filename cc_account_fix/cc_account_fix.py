
import time
from operator import itemgetter

import netsvc
from osv import fields, osv
from osv.orm import except_orm
import pooler
from tools import config
from account import invoice




class fix_invoice(osv.osv):
	_name = "account.invoice"
	_inherit = "account.invoice"
    
    
	def action_move_create(self, cr, uid, ids, *args):
		ait_obj = self.pool.get('account.invoice.tax')
		cur_obj = self.pool.get('res.currency')
		context = {}
		for inv in self.browse(cr, uid, ids):
				if inv.move_id:
						continue
				
				if not inv.date_invoice:
						self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
				company_currency = inv.company_id.currency_id.id
			# create the analytical lines
				line_ids = self.read(cr, uid, [inv.id], ['invoice_line'])[0]['invoice_line']
			# one move line per invoice line
				iml = self._get_analytic_lines(cr, uid, inv.id)
			# check if taxes are all computed
				ctx = context.copy()
				ctx.update({'lang': inv.partner_id.lang})
				compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
				if not inv.tax_line:
						for tax in compute_taxes.values():
								ait_obj.create(cr, uid, tax)
				else:
						tax_key = []
						for tax in inv.tax_line:
								if tax.manual:
										continue
								key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id)
								tax_key.append(key)
								if not key in compute_taxes:
										raise osv.except_osv(_('Warning !'), _('Global taxes defined, but are not in invoice lines !'))
								base = compute_taxes[key]['base']
								if abs(base - tax.base) > inv.company_id.currency_id.rounding:
										raise osv.except_osv(_('Warning !'), _('Tax base different !\nClick on compute to update tax base'))
						for key in compute_taxes:
								if not key in tax_key:
										raise osv.except_osv(_('Warning !'), _('Taxes missing !'))
										
				if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
						raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))
						
			# one move line per tax line
				iml += ait_obj.move_line_get(cr, uid, inv.id)
				
				if inv.type in ('in_invoice', 'in_refund'):
						ref = inv.reference
				else:
						ref = self._convert_ref(cr, uid, inv.number)
						
				diff_currency_p = inv.currency_id.id <> company_currency
			# create one move line for the total and possibly adjust the other lines amount
				total = 0
				total_currency = 0
				for i in iml:
						if inv.currency_id.id != company_currency:
								i['currency_id'] = inv.currency_id.id
								i['amount_currency'] = i['price']
								i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
												company_currency, i['price'],
												context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
						else:
								i['amount_currency'] = False
								i['currency_id'] = False
						i['ref'] = ref
						if inv.type in ('out_invoice','in_refund'):
								total += i['price']
								total_currency += i['amount_currency'] or i['price']
								i['price'] = - i['price']
						else:
								total -= i['price']
								total_currency -= i['amount_currency'] or i['price']
				acc_id = inv.account_id.id

				name = inv['name'] or '/'
				totlines = False
				if inv.payment_term:
						totlines = self.pool.get('account.payment.term').compute(cr,
										uid, inv.payment_term.id, total, inv.date_invoice or False)
				if totlines:
						res_amount_currency = total_currency
						i = 0
						for t in totlines:
								if inv.currency_id.id != company_currency:
										amount_currency = cur_obj.compute(cr, uid,
														company_currency, inv.currency_id.id, t[1])
								else:
										amount_currency = False

				# last line add the diff
										res_amount_currency -= amount_currency or 0
										i += 1
										if i == len(totlines):
												amount_currency += res_amount_currency

										iml.append({
												'type': 'dest',
												'name': name,
												'price': t[1],
												'account_id': acc_id,
												'date_maturity': t[0],
												'amount_currency': diff_currency_p \
																and  amount_currency or False,
												'currency_id': diff_currency_p \
															and inv.currency_id.id or False,
												'ref': ref,
										})
				else:
						iml.append({
							'type': 'dest',
							'name': name,
							'price': total,
							'account_id': acc_id,
							'date_maturity' : inv.date_due or False,
							'amount_currency': diff_currency_p \
											and total_currency or False,
							'currency_id': diff_currency_p \
											and inv.currency_id.id or False,
							'ref': ref
				})
				
				date = inv.date_invoice or time.strftime('%Y-%m-%d')
				part = inv.partner_id.id
				
				line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context={})) ,iml)
				
				if inv.journal_id.group_invoice_lines:
						line2 = {}
						for x, y, l in line:
								tmp = str(l['account_id'])
								tmp += '-'+str(l.get('tax_code_id',"False"))
								tmp += '-'+str(l.get('product_id',"False"))
								tmp += '-'+str(l.get('analytic_account_id',"False"))
								tmp += '-'+str(l.get('date_maturity',"False"))
								
								if tmp in line2:
										am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
										line2[tmp]['debit'] = (am > 0) and am or 0.0
										line2[tmp]['credit'] = (am < 0) and -am or 0.0
										line2[tmp]['tax_amount'] += l['tax_amount']
										line2[tmp]['analytic_lines'] += l['analytic_lines']
								else:
										line2[tmp] = l
						line = []
						for key, val in line2.items():
								line.append((0,0,val))
				
				journal_id = inv.journal_id.id #self._get_journal(cr, uid, {'type': inv['type']})
				journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
				if journal.centralisation:
						raise osv.except_osv(_('UserError'),
										_('Cannot create invoice move on centralised journal'))

				line = self.finalize_invoice_move_lines(cr, uid, inv, line)

				move = {'ref': inv.number, 'line_id': line, 'journal_id': journal_id, 'date': date}
				period_id=inv.period_id and inv.period_id.id or False
				if not period_id:
						fiscalyear_ids= self.pool.get('account.fiscalyear').search(cr,uid,[('date_start','<=',inv.date_invoice or time.strftime('%Y-%m-%d')),('date_stop','>=',inv.date_invoice or time.strftime('%Y-%m-%d')),('company_id','=',inv.company_id.id)])
						if len(fiscalyear_ids):
								period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',inv.date_invoice or time.strftime('%Y-%m-%d')),('date_stop','>=',inv.date_invoice or time.strftime('%Y-%m-%d')),('fiscalyear_id','=',fiscalyear_ids[0])])
						else:
								period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',inv.date_invoice or time.strftime('%Y-%m-%d')),('date_stop','>=',inv.date_invoice or time.strftime('%Y-%m-%d'))])
						if len(period_ids):
								period_id=period_ids[0]
				if period_id:
						move['period_id'] = period_id
						for i in line:
								i[2]['period_id'] = period_id
								
								
								
				move_id = self.pool.get('account.move').create(cr, uid, move, context=context)
				new_move_name = self.pool.get('account.move').browse(cr, uid, move_id).name
            # make the invoice point to that move
				self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name})
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
				self.pool.get('account.move').post(cr, uid, [move_id], context={'invoice':inv})
			
				self._log_event(cr, uid, ids)
		return True
								
		
  
	def action_number(self, cr, uid, ids, *args):
		cr.execute('SELECT id, type, number, move_id, reference ' \
					'FROM account_invoice ' \
					'WHERE id IN %s',
					(tuple(ids),))
		obj_inv = self.browse(cr, uid, ids)[0]
		for (id, invtype, number, move_id, reference) in cr.fetchall():
			if not number:
				tmp_context = {
					'fiscalyear_id' : obj_inv.period_id.fiscalyear_id.id,
				}
				if obj_inv.journal_id.invoice_sequence_id:
					sid = obj_inv.journal_id.invoice_sequence_id.id
					number = self.pool.get('ir.sequence').get_id(cr, uid, sid, 'id=%s', context=tmp_context)
				else:
					number = self.pool.get('ir.sequence').get_id(cr, uid,
																	'account.invoice.' + invtype,
																	'code=%s',
																	context=tmp_context)
				if not number:
					raise osv.except_osv(_('Warning !'), _('There is no active invoice sequence defined for the journal !'))

				if invtype in ('in_invoice', 'in_refund'):
					ref = reference
				else:
					ref = self._convert_ref(cr, uid, number)
				cr.execute('UPDATE account_invoice SET number=%s ' \
						'WHERE id=%s', (number, id))
				cr.execute('UPDATE account_move SET ref=%s ' \
						'WHERE id=%s AND (ref is null OR ref = \'\')',
						(ref, move_id))
				cr.execute('UPDATE account_move_line SET ref=%s ' \
						'WHERE move_id=%s AND (ref is null OR ref = \'\')',
						(ref, move_id))
				cr.execute('UPDATE account_analytic_line SET ref=%s ' \
						'FROM account_move_line ' \
						'WHERE account_move_line.move_id = %s ' \
							'AND account_analytic_line.move_id = account_move_line.id',
							(ref, move_id))
                            
				description=obj_inv.name or False
				if not description:
					self.write(cr, uid, [obj_inv.id], {'name':number})
					
		return True  
fix_invoice()
        


