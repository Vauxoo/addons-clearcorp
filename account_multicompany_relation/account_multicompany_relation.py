# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Mag Guevara. Copyright ClearCorp SA
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

class account_multicompany_relation(osv.osv):
	_name = "account.multicompany.relation"
	_inherit = "account.journal"
	_columns = {
		'origin_account'    :    fields.many2one('account.account', 'Original Account',help='Indicate the original account where the transaction is taking place'),
		'targ_account'      :    fields.many2one('account.account', 'Target Account',help='Indicate the target account where the transaction of the original account has to be seen, this is an account from another company'),
		'origin_journal'    :    fields.many2one('account.journal', 'Original Journal',help='Indicate the original journal where the transaction is taking place'),
		'targ_journal'      :    fields.many2one('account.journal', 'Target Journal',help='Indicate the original account where the transaction is taking place'),
	}
account_multicompany_relation()

class account_journal(osv.osv):
	_name = 'account.journal'
	_inherit = 'account.journal'
	_columns = {
		'journal_mirror'   :   fields.many2one('account.multicompany.relation','Mirror Relation'),
	}
account_journal()

class account_account(osv.osv):
	_name = 'account.account'
	_inherit = 'account.account'
	_columns = {
		'account_mirror'   :   fields.many2one('account.multicompany.relation','Mirror Relation'),
	}
account_account()
