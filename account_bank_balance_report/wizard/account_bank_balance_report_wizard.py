# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv


class accountBankbalanceReportwizard(osv.osv_memory):

    _inherit = "account.report.wiz"
    _name = "bank.balance.wiz"
    _description = "Account Bank Balance Report Wizard"

    _columns = {
        'res_partner_bank_ids': fields.many2one('res.partner.bank',
                                                'Bank Accounts'),
        'period_ids': fields.many2one('account.period', 'Period'),
        'out_format': fields.selection([('pdf', 'PDF')], 'Print Format'),
    }
    _defaults = {
        'journal_ids': [],
        'out_format': 'pdf',
        'filter': 'filter_period',
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        # Read new fields that don't belong to account.report.wiz
        """
            For fields with relations m2o, m2m, it is necessary to extract ids.
            Initial value comes from wizard as a tuple, then extract its id
            and update data['form'] dictionary
        """
        vals = self.read(cr, uid, ids, ['res_partner_bank_ids', 'period_ids'],
                         context=context)[0]
        for field in ['res_partner_bank_ids', 'period_ids']:
            if isinstance(vals[field], tuple):
                vals[field] = vals[field][0]
        data['form'].update(vals)
        return data

    def _print_report(self, cr, uid, ids, data, context=None):
        report_name = 'account_bank_balance_report.report_bank_balance'
        context = context or {}
        # Update data with new values
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context': context
        }
