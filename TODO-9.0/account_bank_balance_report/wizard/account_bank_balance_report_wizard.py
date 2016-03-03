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

from openerp.osv import fields, osv

class accountBankbalanceReportwizard(osv.osv_memory):
    
    _inherit = "account.report.wiz"
    _name = "bank.balance.wiz"
    _description = "Account Bank Balance Report Wizard"
    
    _columns = {
        'res_partner_bank_ids': fields.many2one('res.partner.bank', 'Bank Accounts'),
        'period_ids': fields.many2one('account.period', 'Period'),
        'out_format': fields.selection([('pdf','PDF')], 'Print Format'),
    }
    
    _defaults = {
       'journal_ids':[],
       'out_format': 'pdf',
       'filter': 'filter_period',
       }
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
                    
        #Read new fields that don't belong to account.report.wiz
        """
            For fields with relations m2o, m2m, it is necessary to extract ids. 
            Initial value comes from wizard as a tuple, then extract its id
            and update data['form'] dictionary
        """
        vals = self.read(cr, uid, ids,['res_partner_bank_ids', 'period_ids'], context=context)[0]
        for field in ['res_partner_bank_ids', 'period_ids']:
            if isinstance(vals[field], tuple):
                vals[field] = vals[field][0]
                                
        data['form'].update(vals)
        
        return data
        
    def _print_report(self, cr, uid, ids, data, context=None):
        mimetype = self.pool.get('report.mimetypes')
        report_obj = self.pool.get('ir.actions.report.xml')
        report_name = 'account_bank_balance_report.report_bank_balance'
        
        context = context or {}
        
        #Update data with new values
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context':context
        }
