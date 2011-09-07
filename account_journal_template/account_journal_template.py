# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi. Copyright Camptocamp SA
#    Donors: Hasa Sàrl, Open Net Sàrl and Prisme Solutions Informatique SA
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
import tools
from osv import osv, fields
import addons
import os
from tools import debug

class account_journal_template(osv.osv):
	
	_name = 'account.journal.template'
	_columns = {
	
		'name': fields.char('Journal Name', size=64),
		'code': fields.char('Code', size=5),
		'type': fields.selection([('sale', 'Sale'),('sale_refund','Sale Refund'), ('purchase', 'Purchase'), ('purchase_refund','Purchase Refund'), ('cash', 'Cash'), ('bank', 'Bank and Cheques'), ('general', 'General'), ('situation', 'Opening/Closing Situation'), ('payment', 'Payment method')], 'Type'),
		'allow_date':fields.boolean('Check Date not in the Period'),
		'entry_posted': fields.boolean('Skip \'Draft\' State for Manual Entries'),
		'update_posted': fields.boolean('Allow Cancelling Entries'),
		'group_invoice_lines': fields.boolean('Group Invoice Lines'),
		'currency': fields.many2one('res.currency', 'Currency'),
		'view_id': fields.many2one('account.journal.view', 'Display Mode'),
		'centralisation': fields.boolean('Centralised counterpart'),
		'default_credit_account_id': fields.many2one('account.account', 'Default Credit Account', domain="[('type','!=','view')]", help="It acts as a default account for credit amount"),
		'default_debit_account_id': fields.many2one('account.account', 'Default Debit Account', domain="[('type','!=','view')]", help="It acts as a default account for debit amount"),
		'chart_template_id': fields.many2one('account.chart.template', 'Chart Template', required=True),
	}
account_journal_template()

class WizardMultiChartsAccounts(osv.osv_memory):

	_inherit ='wizard.multi.charts.accounts'
	
	
	def execute(self, cr, uid, ids, context=None):
		
		
		res = super(WizardMultiChartsAccounts, self).execute(cr, uid, ids, context)
		
		#getting the wizard object
		obj_self = self.browse(cr,uid,ids[0])
		
		#getting the id of the company from the wizard
		id_companny = obj_self.company_id.id
		
		#getting the char_id from the wizard object
		id_char_template = obj_self.chart_template_id
		
		#getting the list of journal_templates
		lista = self.pool.get('account.journal.template').search(cr, uid, [('chart_template_id','=',id_char_template)])
		
		
		for x in lista:
			obj = self.pool.get('account.journal.template').browse(cr,uid,x)
			vals = {
				'name' : obj.name,
				'code' : obj.code,
				'type' : obj.type,
				'currency' : obj.currency,
				'allow_date' : obj.allow_date,
				'centralisation' : obj.centralisation,
				'entry_posted' : obj.entry_posted,
				'update_posted' : obj.update_posted,
				'group_invoice_lines' : obj.group_invoice_lines,
				'sequence_id' : obj.sequence_id.id,
				'view_id' : obj.view_id.id,
				'default_credit_account_id': obj.default_credit_account_id.id,
				'default_debit_account_id' : obj.default_debit_account_id.id,
				'company_id': id_companny,
			}
			debug(obj.view_id.id)
			journal = self.pool.get('account.journal')
			journal.create(cr,uid,vals, context=context)
			
			
		return res
	
WizardMultiChartsAccounts()


