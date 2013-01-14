#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import netsvc
from osv import fields, orm
import tools
from tools.translate import _

class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):

        result = super(AccountInvoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        if 'account_id' in result['value']:
            del result['value']['account_id']

        return result

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        result = super(AccountInvoice, self).onchange_journal_id(cr, uid, ids, journal_id, context)

        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)

        if journal.type == 'sale':
            acc_id = journal.default_receivable_account_id.id
        elif journal.type == 'purchase':
            acc_id = journal.default_payable_account_id.id
        elif journal.type == 'sale_refund':
            acc_id = journal.default_payable_account_id.id
        elif journal.type == 'purchase_refund':
            acc_id = journal.default_receivable_account_id.id

        result['value']['account_id'] = acc_id

        return result

    def create(self, cr, uid, vals, context=None):
        if 'journal_id' in vals:
            journal_val_id = vals['journal_id']
            journal_id = self.pool.get('account.journal').search(cr,uid,[('id','=',journal_val_id)])
            journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)

            for journal in journal_obj:
                if journal.type == 'sale':
                    acc_id = journal.default_receivable_account_id.id
                elif journal.type == 'purchase':
                    acc_id = journal.default_payable_account_id.id
                elif journal.type == 'sale_refund':
                    acc_id = journal.default_payable_account_id.id
                elif journal.type == 'purchase_refund':
                    acc_id = journal.default_receivable_account_id.id

                if journal and journal.id:
                    currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
                else:
                    currency_id = False

            if not 'account_id' in vals:
                vals['account_id'] = acc_id

            if not 'currency_id' in vals:
                vals['currency_id'] = currency_id

        return super(AccountInvoice, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):

        if 'journal_id' in vals:
            journal_val_id = vals['journal_id']
            journal_id = self.pool.get('account.journal').search(cr,uid,[('id','=',journal_val_id)])
            journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)

            for journal in journal_obj:
                if journal.type == 'sale':
                    acc_id = journal.default_receivable_account_id.id
                elif journal.type == 'purchase':
                    acc_id = journal.default_payable_account_id.id
                elif journal.type == 'sale_refund':
                    acc_id = journal.default_payable_account_id.id
                elif journal.type == 'purchase_refund':
                    acc_id = journal.default_receivable_account_id.id

                if journal and journal.id:
                    currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
                else:
                    currency_id = False

            if not 'account_id' in vals:
                vals['account_id'] = acc_id

            if not 'currency_id' in vals:
                vals['currency_id'] = currency_id

        return super(AccountInvoice, self).write(cr, uid, ids, vals, context=context)

class AccountJournal(orm.Model):
    _inherit = 'account.journal'

    _columns = {
        'default_receivable_account_id': fields.many2one('account.account', 'Default Receivable Account', domain="[('type','!=','view')]", help="It acts as a default receivable account"),
        'default_payable_account_id': fields.many2one('account.account', 'Default Payable Account', domain="[('type','!=','view')]", help="It acts as a default payable account"),
    }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
