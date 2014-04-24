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
from openerp.tools.translate import _

class accountInvoiceinherit(orm.Model):
    
    _inherit = "account.invoice"
    
    def add_payments(self, cr, uid, ids, context=None):
        line_ids = []
        
        if not ids: return []                
        
        #module_name, id view
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher_prepayment', 'account_voucher_prepayment_wizard')
        #Get invoice id
        inv = self.browse(cr, uid, ids[0], context=context)
        
        #extract move_lines id
        for line in inv.move_id.line_id:
            #line account must match with account invoice
            if line.account_id == inv.account_id:
                line_ids.append(line.id)
        
        #Call wizard             
        return {
            'name':_("Add Payments"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'tree, form',
            'res_model': 'account.voucher.add.payments',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': "[]",
            'context': {               
                'default_partner_id': inv.partner_id.id, #set partner_id
                'default_account_id': inv.account_id.id, #set account_id
                'invoice_move_lines': line_ids, #set move lines
            }
        }