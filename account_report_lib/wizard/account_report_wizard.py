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

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _

class accountCommonwizard (osv.TransientModel):
    
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
    _description = "Account Common Wizard"

    #=======================================================
    
    def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
        res = {}
        if chart_account_id:
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            now = time.strftime('%Y-%m-%d')
            domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
            fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
            res['value'] = {'company_id': company_id, 'fiscalyear_id': fiscalyears and fiscalyears[0] or False}
        return res
    
    #This fields are added, because the account.common.report doesn't have by default    
    _columns = {
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        'account_ids': fields.many2many('account.account', string='Accounts'),
        'journal_ids': fields.many2many('account.journal', string='Journals', required=False), #redefined journal_ids, remove attribute required
        'res_partners_ids': fields.many2many('res.partner', string='Partners',), 
        'historic_strict': fields.boolean('Strict History', help="If selected, will display a historical unreconciled lines, taking into account the end of the period or date selected"),
        'special_period': fields.boolean('Special period', help="Include special period"),    
        'amount_currency': fields.boolean('With Currency', help="It adds the currency column on report if the currency differs from the company currency."),
        'account_base_report':fields.many2one('account.financial.report', string="Account Base Report"), #Filter by account.financial.report only that are sum (view)
        'out_format': fields.selection([('pdf','PDF'),('xls','XLS')], 'Print Format'),
        #This field could be redefined by another wizards, they could add more options
        'sort_selection': fields.selection([('date', 'Date'), ('name', 'Name'),], 'Entries Sorted by',),
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=True),
        'period_from': fields.many2one('account.period', 'Start Period'),
        'period_to': fields.many2one('account.period', 'End Period'),
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves', required=True),
    }
    
    def _check_company_id(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            company_id = wiz.company_id.id
            if wiz.fiscalyear_id and company_id != wiz.fiscalyear_id.company_id.id:
                return False
            if wiz.period_from and company_id != wiz.period_from.company_id.id:
                return False
            if wiz.period_to and company_id != wiz.period_to.company_id.id:
                return False
        return True

    _constraints = [
        (_check_company_id, 'The fiscalyear, periods or chart of account chosen have to belong to the same company.', ['chart_account_id','fiscalyear_id','period_from','period_to']),
    ]
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:context = {}
        res = super(accountCommonwizard, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context.get('active_model', False) == 'account.account':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='chart_account_id']")
            for node in nodes:
                node.set('readonly', '1')
                node.set('help', 'If you print the report from Account list/form view it will not consider Charts of account')
                setup_modifiers(node, res['fields']['chart_account_id'])
            res['arch'] = etree.tostring(doc)
        return res

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {'value': {}}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_date':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res

    def _get_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
        return accounts and accounts[0] or False

    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[])

    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.common.report',context=c),
        'journal_ids': _get_all_journal,
        'res_partners_ids':[],
        'chart_account_id': _get_account,
        'target_move': 'posted',
        
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
    
    def _print_report(self, cr, uid, ids, data, context=None):
        raise (_('Error!'), _('Not implemented.'))
    
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
