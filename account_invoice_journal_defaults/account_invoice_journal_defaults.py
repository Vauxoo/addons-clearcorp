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
from osv import fields, osv
import tools
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _name = 'account.invoice'
    _description = 'Invoice'
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        
        del result['value']['account_id']
        
        return result

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        result = super(account_invoice, self).onchange_journal_id(cr, uid, ids, journal_id, context)
        
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

class account_journal(osv.osv):
    _inherit = 'account.journal'
    _name = 'account.journal'
    _description = 'Journal'
    
    _columns = {
        'default_receivable_account_id': fields.many2one('account.account', 'Default Receivable Account', domain="[('type','!=','view')]", help="It acts as a default receivable account"),
        'default_payable_account_id': fields.many2one('account.account', 'Default Payable Account', domain="[('type','!=','view')]", help="It acts as a default payable account"),
    }




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
