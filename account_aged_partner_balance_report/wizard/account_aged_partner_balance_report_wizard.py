# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import osv, fields
from tools.translate import _

class accountAgedpartnerBalanceWizard(osv.osv_memory):
    _inherit = "account.report.wiz"
    _name = 'aged.partner.balance.wiz'
    _description = 'Account Aged Partner Balance Report'

    _columns = {
        'period_length':fields.integer('Period Length (days)'),
        'direction_selection': fields.selection([('past','Past'),('future','Future')], 'Analysis Direction'),
        'account_type': fields.selection([('customer','Receivable Accounts'),
                                          ('supplier','Payable Accounts'),
                                          ('customer_supplier','Receivable and Payable Accounts')],"Account type",),
    }
    _defaults = {
        'period_length': 30,
        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
        'direction_selection': 'past',
        'filter': 'filter_date',
    }
    
    def pre_print_report(self, cr, uid, ids, data, context=None):       
        if context is None:
            context = {}
            
        # read period_length and direction_selection, because those fields don't belongs to the account.report.wiz
        vals = self.read(cr, uid, ids,['period_length','direction_selection','account_type'], context=context)[0] #this method read the field and included it in the form (account.common.report has this method)                       
        data['form'].update(vals)
        
        return data

    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        mimetype = self.pool.get('report.mimetypes')
        report_obj = self.pool.get('ir.actions.report.xml')
        report_name = ''
        
        if context is None:
            context = {}
                    
        # we update form with display account value
        data = self.pre_print_report(cr, uid, ids, data, context=context)

        period_length = data['form']['period_length']

        if period_length <= 0:
            raise osv.except_osv(_('UserError'), _('You must enter a period length that cannot be 0 or below !'))
        
        #In this section, create interval times, depends of period length parameter
        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)
                
       #=======================================================================
        # onchange_in_format method changes variable out_format depending of 
        # which in_format is choosed. 
        # If out_format is pdf -> call record in odt format and if it's choosed
        # ods or xls -> call record in ods format.
        # ods and xls format are editable format, because they are arranged 
        # to be changed by user and, for example, user can check and change info.    
        #=======================================================================
       
        #=======================================================================
        # If mimetype is PDF -> out_format = PDF (search odt record)
        # If mimetype is xls or ods -> search ods record. 
        # If record doesn't exist, return a error.
        #=======================================================================
        
        #=======================================================================
        # Create two differents records for each format, depends of the out_format
        # selected, choose one of this records
        #=======================================================================
        
        #1. Find out_format selected
        out_format_obj = mimetype.browse(cr, uid, [int(data['form']['out_format'])], context)[0]

        #2. Check out_format and set report_name for each format
        if out_format_obj.code == 'oo-pdf':
            report_name = 'account_aged_partner_balance_odt' 
           
        elif out_format_obj.code == 'oo-xls' or out_format_obj.code == 'oo-ods': 
            report_name = 'account_aged_partner_balance_ods'
        
        # If there not exist name, it's because not exist a record for this format   
        if report_name == '':
            raise osv.except_osv(_('Error !'), _('There is no template defined for the selected format. Check if aeroo report exist.'))
                
        else:
            #Search record that match with the name, and get some extra information
            report_xml_id = report_obj.search(cr, uid, [('report_name','=', report_name)],context=context)
            report_xml = report_obj.browse(cr, uid, report_xml_id, context=context)[0]
            data.update({'model': report_xml.model, 'report_type':'aeroo', 'id': report_xml.id})
            
            #Write out_format choosed in wizard
            report_xml.write({'out_format': out_format_obj.id}, context=context)
           
            return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'datas': data,
                'context':context
            }
