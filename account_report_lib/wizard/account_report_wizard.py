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

class accountCommonwizard (orm.Model):
    
    """
        This class is the base for the wizard report. If is necessary
        add another field, add for this class.
        The fields that add for the account.common.report inherit are:
            chart_account_id, company_id, fiscalyear_id, filter, period_from, period_to, journal_ids,
            date_from, date_to, target_move.
        
        Also, add the methods:
            onchange_chart_id, _check_company_id, fields_view_get, onchange_filter, _get_account, _get_fiscalyear
            _get_all_journal, _build_contexts, _print_report, check_report
                
    """
    _name = "account.report.wiz"
    _inherit = "account.common.report"
    _description = "Account Common Wizard"
    
    """
        With the inclusion of reports aeroo project, include the variable "out_format" which allows printing in different formats 
        (including those of Microsoft xls, doc and PDF). It is the inclusion of these formats as a requirement for printing
        accounting reports
        
        The options for this variable are: 
            * PDF (this format call internally a odt template, pdf isn't a editable document)
            * XLS and ODS: This format provide a editable document (internally call a ods template)
        
        Include two new methods: _out_format_get and in_format_get. Both extract report's name from context and get compatibles
        formats for report. in_format_get is implemented in each wizard.  
    """
    
    #===========================================================================
    # For field out_format, it has three options: PDF, XLS and ODS. This options
    # provide a editable and no-editable document. If user needs to edit some 
    # account financial report, then use options xls or ods. If user doesn't need 
    # to edit the report, use option PDF.
    #===========================================================================    
    
    #===========================================================================
    # The out_format need to work two record for each report.    
    # This is because with aeroo reports the ods template is very complicated 
    # to word, specially with images and styles. 
    # 
    # So, to convert to pdf, it's necessary create a record with a odt file 
    # (as a template) and to convert to ods or xls, it's necessary create a 
    # record with a ods file (as a template). 
    # 
    # The idea is that user use odt or xls file for "work" in report, for example, 
    # recalculate values or compute again the results. 
    # The method search by report's name (set in context)
    #
    # out_format search in list of records. One of them must match with in_format,
    # for example, if out_format = PDF, it must exist a record where in_format = odt.
    # If out_format is xls or ods, it must exist a record where in_format = ods. 
    #
    # in_format ensures that exist a template created in system. This "checking"
    # is made in each wizard for each report, because it's necessary report's name.
    #===========================================================================
    
    def out_format_get (self, cr, uid, context={}):
        obj = self.pool.get('report.mimetypes')
        ids = []
        list = []
        
        ids = obj.search(cr, uid, ['|', '|',('code','=','oo-xls'), ('code','=','oo-ods'),('code','=','oo-pdf')])
        #only include format pdf that match with ods format.
        for type in obj.browse(cr, uid, ids, context=context):
            if type.code == 'oo-pdf' and type.compatible_types == 'oo-odt':
                list.append(type.id)
            elif type.code == 'oo-xls' or type.code == 'oo-ods':
                list.append(type.id)

        # If read method isn't call, the value for out_format "disappear",
        # the value is preserved, but disappears from the screen (a rare bug)
        res = obj.read(cr, uid, list, ['name'], context)
        return [(str(r['id']), r['name']) for r in res]    

    #=======================================================
    
    #This fields are added, because the account.common.report doesn't have by default    
    _columns = {
        'account_ids': fields.many2many('account.account', string='Accounts'),
        'journal_ids': fields.many2many('account.journal', string='Journals',), #redefined journal_ids, remove attribute required
        'res_partners_ids': fields.many2many('res.partner', string='Partners',), 
        'historic_strict': fields.boolean('Strict History', help="If selected, will display a historical unreconciled lines, taking into account the end of the period or date selected"),
        'special_period': fields.boolean('Special period', help="Include special period"),    
        'amount_currency': fields.boolean('With Currency', help="It adds the currency column on report if the currency differs from the company currency."),
        'account_base_report':fields.many2one('account.financial.report', string="Account Base Report"), #Filter by account.financial.report only that are sum (view)
        'out_format': fields.selection(out_format_get, 'Print Format'),
        #This field could be redefined by another wizards, they could add more options
        'sort_selection': fields.selection([('date', 'Date'), ('name', 'Name'),], 'Entries Sorted by',),        
    }
    
    _defaults = {
        'journal_ids':[],
        'res_partners_ids':[],
    }
    
    #Redefine this method, because in the "original" take both periods (start and end) and some reports don't need both periods
    #Add the new fields that not included in the account.common.report. 
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        
        #new fields
        result['account_ids'] = 'account_ids' in data['form'] and data['form']['account_ids'] or False
        result['historic_strict'] = 'historic_strict' in data['form'] and data['form']['historic_strict'] or False
        result['special_period'] = 'special_period' in data['form'] and data['form']['special_period'] or False
        result['amount_currency'] = 'amount_currency' in data['form'] and data['form']['amount_currency'] or False
        result['account_base_report'] = 'account_base_report' in data['form'] and data['form']['account_base_report'] or False
        result['out_format'] = 'out_format' in data['form'] and data['form']['out_format'] or False
        result['sort_selection'] = 'sort_selection' in data['form'] and data['form']['sort_selection'] or False
        result['res_partners_ids'] = 'res_partners_ids' in data['form'] and data['form']['res_partners_ids'] or False
        result['account_type'] = 'account_type' in data['form'] and data['form']['account_type'] or False
              
        if data['form']['filter'] == 'filter_date':
            result['date_from'] = data['form']['date_from']
            result['date_to'] = data['form']['date_to']
            
        elif data['form']['filter'] == 'filter_period':          
            result['period_from'] = data['form']['period_from']
            result['period_to'] = data['form']['period_to']
            
        return result 
    
    #Add the new fields 
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['report_name'] = context.get('report_name',False) # -> Include report's name to include print formats
        
        #include new fields
        data['form'] = self.read(cr, uid, ids, ['account_base_report','amount_currency','special_period','historic_strict','account_ids','date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move', 'out_format','sort_selection', 'res_partners_ids','account_type'], context=context)[0]
        # The fields that are relations (many2one, many2many, one2many needs extracted 
        # the id and work with the id in the form)
        # Also, selection fields, because they are a tuple with id, name.
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to','account_ids','account_base_report','out_format','journal_ids','sort_selection','res_partners_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]

        #Check if the fields exist, otherwise put false in the field.
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = used_context
        
        #In each report redefine the _print_report, that receive the data and
        #print the report in each module. The data argument is already build 
        return self._print_report(cr, uid, ids, data, context=context)         
        
    