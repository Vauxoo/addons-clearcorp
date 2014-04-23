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

class accountVoucheraddPaymentwizard (osv.osv_memory):
    
    _name = "account.voucher.add.payments"
    _description = "Account Voucher Add Payments Wizard"
    
    #===========================================================================
    # partner_id and account_id comes from main window. By default property,
    # set values from main window and pass them to wizard.
    # They also are used in xml, to build principal domain.
    #===========================================================================
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        'account_id': fields.many2one('account.account', 'Account'), #it's is for apply the domain in xml.
        'move_lines': fields.many2many('account.move.line', 'move_lines_prepayment', required=True, string="Move Lines"),
    }
  
    def action_reconcile(self, cr, uid, ids, context=None):        
        #module_name, id view
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_account_move_line_reconcile_full')
        
        #Get move_lines from invoice
        invoice_move_lines_ids = context['invoice_move_lines']        
        
        #Get move_lines from wizard
        wizard_move_lines = self.read(cr, uid, ids, ['move_lines'], context=context)[0] #return a dictionary   
        wizard_move_lines_ids = wizard_move_lines['move_lines'] 
        
        #Put all ids together        
        all_ids = wizard_move_lines_ids + invoice_move_lines_ids
        #Update context        
        context.update({'active_ids': all_ids})
  
        return {
            'name':_("Reconcile"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.move.line.reconcile',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': "[]",
            'context':context,                
        }
        
        