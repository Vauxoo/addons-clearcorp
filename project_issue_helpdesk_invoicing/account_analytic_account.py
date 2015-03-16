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
from openerp.osv import osv, fields
from openerp import tools
from openerp.addons.decimal_precision import decimal_precision as dp
from datetime import datetime, timedelta

class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"
    
    def _get_invoice_price(self, cr, uid, account, date,start_time,end_time, product_id,categ_id,qty,service_type, context = {}):
        regular_hours=0.0
        extra_hours=0.0
        amount=0.0
        pricelist_obj=self.pool.get('contract.pricelist')
        holiday_state=False
        date_number=datetime.strptime(date, '%Y-%m-%d').weekday()
        holidays=account.holidays_calendar_id.holiday_ids
        if holidays:
            for holiday in holidays:
                if holiday.date==date:
                    holiday_state=True
                    break
        else:
            holiday_state=False
        schedules=account.regular_schedule_id.attendance_ids
        if schedules:
            for schedule in schedules:
                if str(date_number)==schedule.dayofweek:
                    if start_time>=schedule.hour_from and end_time<=schedule.hour_to:
                        regular_hours=qty
                        extra_hours=0.0
                        break
                    elif start_time<schedule.hour_from and end_time>schedule.hour_to:
                        regular_hours=qty-(schedule.hour_from-start_time)-(end_time-schedule.hour_to)
                        extra_hours=(schedule.hour_from-start_time)+(end_time-schedule.hour_to)
                        break
                    elif start_time<schedule.hour_from and end_time<=schedule.hour_to and end_time>=schedule.hour_from:
                        if schedule.hour_from<>schedule.hour_to:
                            regular_hours=qty-(schedule.hour_from-start_time)
                            extra_hours=(schedule.hour_from-start_time)
                        else:
                            regular_hours=0.0
                            extra_hours=(schedule.hour_from-start_time)
                        break
                    elif start_time>=schedule.hour_from and start_time<=schedule.hour_to and end_time>schedule.hour_to:
                        if schedule.hour_from<>schedule.hour_to:
                            regular_hours=qty-(end_time-schedule.hour_to)
                            extra_hours=(end_time-schedule.hour_to)
                        else:
                            regular_hours=0.0
                            extra_hours=(end_time-schedule.hour_to)
                    elif (start_time<schedule.hour_from and end_time<schedule.hour_from) or (start_time>schedule.hour_to and end_time>schedule.hour_to):
                        extra_hours=qty
                        regular_hours=0.0
                        break
                else:
                    regular_hours=qty
        else:
            regular_hours=qty

        pricelist_product_ids=pricelist_obj.search(cr,uid,[('contract_id','=', account.id),('product_id','=', product_id)])
        pricelist_category_ids=pricelist_obj.search(cr,uid,[('contract_id','=', account.id),('categ_id','=', categ_id)])
        
        if pricelist_product_ids or pricelist_category_ids:
            if pricelist_product_ids and pricelist_category_ids:
                pricelist=pricelist_obj.browse(cr, uid, pricelist_product_ids, context=context)
            elif not pricelist_product_ids and pricelist_category_ids:
                pricelist=pricelist_obj.browse(cr, uid, pricelist_category_ids, context=context)
            elif  pricelist_product_ids and not pricelist_category_ids:
                pricelist=pricelist_obj.browse(cr, uid, pricelist_product_ids, context=context)
            
            for list in pricelist:
                if service_type=='expert':
                    if holiday_state==True:
                        amount=list.technical_rate*list.holiday_multiplier*qty
                    elif holiday_state==False:
                        amount=(list.technical_rate*list.overtime_multiplier*extra_hours)+(list.technical_rate*regular_hours)
                elif service_type=='assistant':
                    if holiday_state==True:
                        amount=list.assistant_rate*list.holiday_multiplier
                    elif holiday_state==False:
                        amount=(list.assistant_rate*list.overtime_multiplier*extra_hours)+(list.assistant_rate*regular_hours)
        return amount

    def _analysis_all(self, cr, uid, ids, fields, arg, context=None):
        total=0.0
        res=super(account_analytic_account,self)._analysis_all(cr, uid, ids, fields, arg, context)
        accounts = self.browse(cr, uid, ids, context=context)
        for f in fields:
            if f == 'ca_to_invoice':
                for account in accounts:
                    if account.pricelist_ids:
                        cr.execute("""
                            SELECT line.to_invoice, sum(line.unit_amount), line.name,sheet.issue_id,issue.categ_id,issue.product_id,line.date,sheet.service_type,sheet.start_time,sheet.end_time
                            FROM project_issue issue
                            LEFT JOIN hr_analytic_timesheet sheet on (issue.id=sheet.issue_id)
                            LEFT JOIN account_analytic_line line on (line.id=sheet.line_id)
                            LEFT JOIN account_analytic_journal journal ON (journal.id = line.journal_id)
                            WHERE account_id = %s AND journal.type != 'purchase'
                                  AND line.invoice_id IS NULL
                                  AND to_invoice IS NOT NULL
                            GROUP BY line.to_invoice, line.product_uom_id, line.name,sheet.service_type,line.date,sheet.start_time,sheet.end_time,sheet.issue_id,issue.categ_id,issue.product_id""", (account.id,))
                        for factor_id, qty, line_name, issue_id,categ_id,product_id, date, service_type, start_time,end_time in cr.fetchall():
                                total+=self._get_invoice_price(cr, uid, account, date,start_time,end_time, product_id,categ_id,qty,service_type, context)
                        res[account.id][f] = total
        return res

    _columns = {
        'ca_to_invoice': fields.function(_analysis_all, multi='analytic_analysis', type='float', string='Uninvoiced Amount',
            help="If invoice from analytic account, the remaining amount you can invoice to the customer based on the total costs.",
            digits_compute=dp.get_precision('Account')),
        'ca_theorical': fields.function(_analysis_all, multi='analytic_analysis', type='float', string='Theoretical Revenue',
            help="Based on the costs you had on the project, what would have been the revenue if all these costs have been invoiced at the normal sale price provided by the pricelist.",
            digits_compute=dp.get_precision('Account')),
        'hours_quantity': fields.function(_analysis_all, multi='analytic_analysis', type='float', string='Total Worked Time',
            help="Number of time you spent on the analytic account (from timesheet). It computes quantities on all journal of type 'general'."),
        'last_invoice_date': fields.function(_analysis_all, multi='analytic_analysis', type='date', string='Last Invoice Date',
            help="If invoice from the costs, this is the date of the latest invoiced."),
        'last_worked_invoiced_date': fields.function(_analysis_all, multi='analytic_analysis', type='date', string='Date of Last Invoiced Cost',
            help="If invoice from the costs, this is the date of the latest work or cost that have been invoiced."),
        'last_worked_date': fields.function(_analysis_all, multi='analytic_analysis', type='date', string='Date of Last Cost/Work',
            help="Date of the latest work done on this account."),
        'hours_qtt_non_invoiced': fields.function(_analysis_all, multi='analytic_analysis', type='float', string='Uninvoiced Time',
            help="Number of time (hours/days) (from journal of type 'general') that can be invoiced if you invoice based on analytic account."),
        'month_ids': fields.function(_analysis_all, multi='analytic_analysis', type='many2many', relation='account_analytic_analysis.summary.month', string='Month'),
        'user_ids': fields.function(_analysis_all, multi='analytic_analysis', type="many2many", relation='account_analytic_analysis.summary.user', string='User'),
                }
class account_invoice_report(osv.osv):
    _inherit = "account.invoice.report"
    _columns = {
             'porcent_variation_margin': fields.float(string="Variation Margin(%)", readonly=True),
             'variation_margin': fields.float(string="Variation Margin", readonly=True)
             }
    _depends = {
         'account.invoice.line': ['porcent_variation_margin','variation_margin'],
    }
     
    def _select(
         self):
        return  super(account_invoice_report, self)._select() + ", sub.porcent_variation_margin as porcent_variation_margin, sub.variation_margin as variation_margin"
    
    def _sub_select(self):
        return  super(account_invoice_report, self)._sub_select() + ", ail.porcent_variation_margin as porcent_variation_margin, ail.variation_margin as variation_margin"
    
    def _group_by(self):
        return super(account_invoice_report, self)._group_by() + ", ail.porcent_variation_margin, ail.variation_margin"
    
class account_analytic_line(osv.osv):
    _inherit = 'account.analytic.line'

class ProjectIssue(osv.osv):
    _inherit = 'project.issue'
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result={}
        domain=[]
        result = super(ProjectIssue, self).onchange_partner_id(cr, uid, ids, partner_id)
        if partner_id:
            domain.append(('type', '!=', 'view'))
            domain.append(('partner_id', '=',partner_id))
            contract_ids = self.pool.get('account.analytic.account').search(cr,uid,[('partner_id','=',partner_id)])
            result.update({'domain':{'analytic_account_id':domain}})
            if contract_ids:
                result['value'].update({'analytic_account_id':contract_ids[0]})
            else:
                result['value'].update({'analytic_account_id':False})
        return result
    
    def onchange_branch_id(self, cr, uid, ids, branch_id, context=None):
        result={}
        domain=[]
        result = super(ProjectIssue, self).onchange_branch_id(cr, uid, ids, branch_id)
        if branch_id:
            domain.append(('type', '!=', 'view'))
            domain.append(('branch_ids.id', '=',branch_id))
            contract_ids = self.pool.get('account.analytic.account').search(cr,uid,[('branch_ids.id','=',branch_id)])
            result.update({'domain':{'analytic_account_id':domain}})
            if contract_ids:
                result['value'].update({'analytic_account_id':contract_ids[0]})
            else:
                result['value'].update({'analytic_account_id':False})
        return result