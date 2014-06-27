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
from tools.translate import _

class accountInvoiceinherit(orm.Model):
    
    _inherit = 'account.invoice'

    def invoice_validate(self, cr, uid, ids, context=None):
        #Check if user is in group 'group_account_invoice_limit_discount'
        is_in_group = self.pool.get('res.users').has_group(cr, uid, 'account_invoice_limit_discount.group_account_invoice_limit_discount')
        
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.type == 'out_invoice' or invoice.type == 'out_refund':
                if not is_in_group:
                    #Get company for user currently logged
                    company_user = self.pool.get('res.users').browse(cr, uid, uid).company_id 
                    max_company_discount = company_user.max_discount
                    
                    for invoice in self.browse(cr, uid, ids, context=context):
                        for line in invoice.invoice_line: 
                            if line.discount > max_company_discount:
                                raise osv.except_osv(_("Discount Exceeded!"), _("The discount of invoice exceeds the limit of maximum discount %s of the company") % (str(max_company_discount)))
                
        return super(accountInvoiceinherit, self).invoice_validate(cr, uid, ids, context=context)