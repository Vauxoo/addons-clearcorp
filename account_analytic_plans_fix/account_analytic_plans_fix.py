# -*- encoding: utf-8 -*-
##############################################################################
#
#    account_analytic_plans_fix.py
#    account_analytic_plans_fix
#    First author: Carlos Vásquez <carlos.vasquez@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2011-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without modification, are
#    permitted provided that the following conditions are met:
#    
#       1. Redistributions of source code must retain the above copyright notice, this list of
#          conditions and the following disclaimer.
#    
#       2. Redistributions in binary form must reproduce the above copyright notice, this list
#          of conditions and the following disclaimer in the documentation and/or other materials
#          provided with the distribution.
#    
#    THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ``AS IS'' AND ANY EXPRESS OR IMPLIED
#    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#    
#    The views and conclusions contained in the software and documentation are those of the
#    authors and should not be interpreted as representing official policies, either expressed
#    or implied, of ClearCorp S.A..
#    
##############################################################################

from osv import osv,fields

class account_analytic_plans_fix_move_line(osv.osv):
	'''
	fixes move line manual entry view
	'''
	_name = 'account.move.line'
	_inherit = 'account.move.line'


	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		journal_pool = self.pool.get('account.journal')
		if context is None:
			context = {}
		result = super(account_move_line, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
		if view_type != 'tree':
			#Remove the toolbar from the form view
			if view_type == 'form':
				if result.get('toolbar', False):
					result['toolbar']['action'] = []
			#Restrict the list of journal view in search view
			if view_type == 'search' and result['fields'].get('journal_id', False):
				result['fields']['journal_id']['selection'] = journal_pool.name_search(cr, uid, '', [], context=context)
				ctx = context.copy()
				#we add the refunds journal in the selection field of journal
				if context.get('journal_type', False) == 'sale':
					ctx.update({'journal_type': 'sale_refund'})
					result['fields']['journal_id']['selection'] += journal_pool.name_search(cr, uid, '', [], context=ctx)
				elif context.get('journal_type', False) == 'purchase':
					ctx.update({'journal_type': 'purchase_refund'})
					result['fields']['journal_id']['selection'] += journal_pool.name_search(cr, uid, '', [], context=ctx)
			return result
		if context.get('view_mode', False):
			return result
		fld = []
		fields = {}
		flds = []
		title = _("Accounting Entries") #self.view_header_get(cr, uid, view_id, view_type, context)
		xml = '''<?xml version="1.0"?>\n<tree string="%s" editable="top" refresh="5" on_write="on_create_write" colors="red:state==\'draft\';black:state==\'valid\'">\n\t''' % (title)

		ids = journal_pool.search(cr, uid, [])
		journals = journal_pool.browse(cr, uid, ids, context=context)
		all_journal = [None]
		common_fields = {}
		total = len(journals)
		for journal in journals:
			all_journal.append(journal.id)
			for field in journal.view_id.columns_id:
				if not field.field in fields:
					fields[field.field] = [journal.id]
					fld.append((field.field, field.sequence, field.name))
					flds.append(field.field)
					common_fields[field.field] = 1
				else:
					fields.get(field.field).append(journal.id)
					common_fields[field.field] = common_fields[field.field] + 1
		fld.append(('period_id', 3, _('Period')))
		fld.append(('journal_id', 10, _('Journal')))
		flds.append('period_id')
		flds.append('journal_id')
		fields['period_id'] = all_journal
		fields['journal_id'] = all_journal
		fld = sorted(fld, key=itemgetter(1))
		widths = {
			'statement_id': 50,
			'state': 60,
			'tax_code_id': 50,
			'move_id': 40,
		}
		for field_it in fld:
			field = field_it[0]
			if common_fields.get(field) == total:
				fields.get(field).append(None)
#            if field=='state':
#                state = 'colors="red:state==\'draft\'"'
			attrs = []
			if field == 'debit':
				attrs.append('sum = "%s"' % _("Total debit"))

			elif field == 'credit':
				attrs.append('sum = "%s"' % _("Total credit"))

			elif field == 'move_id':
				attrs.append('required = "False"')

			elif field == 'account_tax_id':
				attrs.append('domain="[(\'parent_id\', \'=\' ,False)]"')
				attrs.append("context=\"{'journal_id': journal_id}\"")

			elif field == 'account_id' and journal.id:
				attrs.append('domain="[(\'journal_id\', \'=\', '+str(journal.id)+'),(\'type\',\'&lt;&gt;\',\'view\'), (\'type\',\'&lt;&gt;\',\'closed\')]" on_change="onchange_account_id(account_id, partner_id)"')

			elif field == 'partner_id':
				attrs.append('on_change="onchange_partner_id(move_id, partner_id, account_id, debit, credit, date, journal_id)"')

			elif field == 'journal_id':
				attrs.append("context=\"{'journal_id': journal_id}\"")

			elif field == 'statement_id':
				attrs.append("domain=\"[('state', '!=', 'confirm'),('journal_id.type', '=', 'bank')]\"")

			elif field == 'date':
				attrs.append('on_change="onchange_date(date)"')

			elif field == 'analytic_account_id':
				attrs.append('''groups="analytic.group_analytic_accounting"''') # Currently it is not working due to framework problem may be ..

			if field in ('amount_currency', 'currency_id'):
				attrs.append('on_change="onchange_currency(account_id, amount_currency, currency_id, date, journal_id)"')
				attrs.append('''attrs="{'readonly': [('state', '=', 'valid')]}"''')

			if field in widths:
				attrs.append('width="'+str(widths[field])+'"')

			if field in ('journal_id',):
				attrs.append("invisible=\"context.get('journal_id', False)\"")
			elif field in ('period_id',):
				attrs.append("invisible=\"context.get('period_id', False)\"")
			else:
				attrs.append("invisible=\"context.get('visible_id') not in %s\"" % (fields.get(field)))
			xml += '''<field name="%s" %s/>\n''' % (field,' '.join(attrs))

		xml += '''</tree>'''
		result['arch'] = xml
		result['fields'] = self.fields_get(cr, uid, flds, context)
		return result
	
account_analytic_plans_fix_move_line()
