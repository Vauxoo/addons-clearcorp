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
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from datetime import datetime


class PayWizard(osv.TransientModel):
    _name = 'sale.commission.pay.wizard'

    def _get_interval_period(
            self, cr, uid, end_period, start_period=None, context=None):
        period_obj = self.pool.get('account.period')
        period_list = []
        # Both start and end period are available
        if start_period and end_period:
            period_list = period_obj.search(
                cr, uid, [('date_start', '>=', start_period.date_start),
                          ('date_stop', '<=', end_period.date_start),
                          ('special', '=', False)], context=context)
        # All periods going back until reaching openning period
        elif not start_period and end_period:
            fiscal_year = end_period.fiscalyear_id.id
            period_list = period_obj.search(
                cr, uid, [('fiscalyear_id', '=', fiscal_year),
                          ('date_stop', '<=', end_period.date_stop),
                          ('special', '=', False)], context=context)
        return period_list

    def _invoices_without_commission(
            self, cr, uid, id, member, rule, period_ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        rule_line_obj = self.pool.get('sale.commission.rule.line')
        commission_obj = self.pool.get('sale.commission.commission')
        commission_ids = []
        # Get the invoices of the user without commission
        cr.execute("""SELECT INV.id
                    FROM account_invoice AS INV
                    WHERE INV.id NOT IN
                        (SELECT COM.invoice_id
                        FROM sale_commission_commission AS COM) AND
                        INV.type = 'out_invoice' AND
                        INV.user_id = %s AND
                        INV.period_id IN %s""", [member.id, tuple(period_ids)])
        invoices_no_commission_ids = [item[0] for item in cr.fetchall()]
        invoices_no_commission = invoice_obj.browse(
            cr, uid, invoices_no_commission_ids, context=context)
        # Get and order the rule_lines by sequence
        rule_line_ids = rule_line_obj.search(
            cr, uid, [('commission_rule_id', '=', rule.id)],
            order='sequence asc', context=context)
        rule_lines = rule_line_obj.browse(
            cr, uid, rule_line_ids, context=context)
        sales_dict = {}
        for invoice in invoices_no_commission:
            if invoice.period_id.id not in sales_dict:
                # Get the invoices of the user
                period_invoices_ids = invoice_obj.search(
                    cr, uid, [('user_id', '=', member.id),
                              ('period_id', '=', invoice.period_id.id)],
                    context=context)
                # Get the total sales for the period
                cr.execute(
                    """SELECT SUM(INV.amount_untaxed) AS amount_untaxed
                       FROM account_invoice AS INV
                       WHERE INV.id IN %s;""", [tuple(period_invoices_ids)])
                total_sales = cr.fetchall()[0][0]
                sales_dict[invoice.period_id.id] = total_sales
            else:
                total_sales = sales_dict[invoice.period_id.id]
            for payment in invoice.payment_ids:
                total_credit = 0.0
                if payment.journal_id and payment.journal_id.pay_commission:
                    if not payment.commission:
                        # Compute the amount of credit that correspond to
                        # the invoice discounted total
                        total_credit = payment.credit * \
                            invoice.amount_untaxed / invoice.amount_total
                    if total_credit > 0.0:
                        if invoice.force_commission:
                            amount = total_credit * \
                                     invoice.commission_percentage / 100
                            exp_days = relativedelta(
                                days=invoice.post_expiration_days)
                            if amount == 0.0:
                                state = 'paid'
                            elif invoice.date_due:
                                inv_date = datetime.strptime(
                                    invoice.date_due, '%Y-%m-%d')
                                payment_date = datetime.strptime(
                                    payment.date, '%Y-%m-%d')
                                if payment_date > inv_date + exp_days:
                                    state = 'expired'
                                else:
                                    state = 'new'
                            else:
                                state = 'expired'
                            values = {
                                'invoice_id': invoice.id,
                                'payment_id': payment.id,
                                'state': state,
                                'user_id': member.id,
                                'amount_base': total_credit,
                                'amount': amount,
                                'invoice_commission_percentage':
                                    invoice.commission_percentage,
                            }
                            commission_id = commission_obj.create(
                                cr, uid, values, context=context)
                            commission_ids.append(commission_id)
                        else:
                            for rule_line in rule_lines:
                                result = True
                                if rule_line.partner_category_id:
                                    if rule_line.partner_category_id not in \
                                            invoice.partner_id.category_id:
                                        result = result and False
                                if rule_line.pricelist_id:
                                    if invoice.pricelist_id:
                                        if not invoice.pricelist_id.id == \
                                                rule_line.pricelist_id.id:
                                            result = result and False
                                    else:
                                        result = result and False
                                if rule_line.payment_term_id:
                                    if invoice.payment_term:
                                        if not invoice.payment_term.id == \
                                                rule_line.payment_term_id:
                                            result = result and False
                                    else:
                                        result = result and False
                                if rule_line.max_discount > 0.0:
                                    if invoice.invoice_discount > \
                                            rule_line.max_discount:
                                        result = result and False
                                if rule_line.monthly_sales > 0.0:
                                    if total_sales < rule_line.monthly_sales:
                                        result = result and False
                                if result:
                                    if rule_line.commission_percentage and \
                                            total_credit:
                                        amount = total_credit * \
                                            rule_line.commission_percentage / \
                                            100
                                    else:
                                        amount = 0.0
                                    exp_days = relativedelta(
                                        days=rule.post_expiration_days)
                                    if amount == 0.0:
                                        state = 'paid'
                                    elif invoice.date_due:
                                        inv_date = datetime.strptime(
                                            invoice.date_due, '%Y-%m-%d')
                                        payment_date = datetime.strptime(
                                            payment.date, '%Y-%m-%d')
                                        if payment_date > inv_date + exp_days:
                                            state = 'expired'
                                        else:
                                            state = 'new'
                                    else:
                                        state = 'expired'
                                    values = {
                                        'invoice_id': invoice.id,
                                        'payment_id': payment.id,
                                        'state': state,
                                        'user_id': member.id,
                                        'amount_base': total_credit,
                                        'amount': amount,
                                        'invoice_commission_percentage':
                                            rule_line.commission_percentage,
                                    }
                                    commission_id = commission_obj.create(
                                        cr, uid, values, context=context)
                                    commission_ids.append(commission_id)
                                    break
        return commission_ids

    def _invoices_with_commission(self, cr, uid, id, member, rule, period_ids,
                                  context=None):
        invoice_obj = self.pool.get('account.invoice')
        rule_line_obj = self.pool.get('sale.commission.rule.line')
        commission_obj = self.pool.get('sale.commission.commission')
        commission_ids = []

        # Get the invoices of the user without commission
        cr.execute("""SELECT INV.id
                    FROM account_invoice AS INV
                    WHERE INV.id IN
                        (SELECT COM.invoice_id
                        FROM sale_commission_commission AS COM) AND
                        INV.type = 'out_invoice' AND
                        INV.user_id = %s AND
                        INV.period_id IN %s""", [member.id, tuple(period_ids)])
        invoices_commission_ids = [item[0] for item in cr.fetchall()]
        invoices_commission = invoice_obj.browse(cr, uid,
                                                 invoices_commission_ids,
                                                 context=context)
        # Get and order the rule_lines by sequence
        rule_line_ids = rule_line_obj.search(cr, uid, [
            ('commission_rule_id', '=', rule.id)],
                                             order='sequence asc',
                                             context=context)
        rule_lines = rule_line_obj.browse(cr, uid, rule_line_ids,
                                          context=context)
        sales_dict = {}
        for invoice in invoices_commission:
            if invoice.period_id.id not in sales_dict:
                # Get the invoices of the user
                period_invoices_ids = invoice_obj.search(cr, uid, [
                    ('user_id', '=', member.id),
                    ('period_id', '=', invoice.period_id.id)], context=context)
                # Get the total sales for the period
                cr.execute("""SELECT SUM(INV.amount_untaxed) AS amount_untaxed
                            FROM account_invoice AS INV
                            WHERE INV.id IN %s;""",
                           [tuple(period_invoices_ids)])
                total_sales = cr.fetchall()[0][0]
                sales_dict[invoice.period_id.id] = total_sales
            else:
                total_sales = sales_dict[invoice.period_id.id]
            for payment in invoice.payment_ids:
                total_credit = 0.0
                if payment.journal_id and payment.journal_id.pay_commission:
                    if not payment.commission:
                        # Compute the amount of credit that correspond to
                        # the invoice discounted total
                        total_credit = payment.credit * \
                            invoice.amount_untaxed / invoice.amount_total
                    if total_credit > 0.0:
                        if invoice.force_commission:
                            amount = total_credit * \
                                invoice.commission_percentage / 100
                            exp_days = relativedelta(
                                days=invoice.post_expiration_days)
                            if invoice.date_due:
                                inv_date = datetime.strptime(invoice.date_due,
                                                             '%Y-%m-%d')
                                payment_date = datetime.strptime(payment.date,
                                                                 '%Y-%m-%d')
                                if payment_date > inv_date + exp_days:
                                    state = 'expired'
                                else:
                                    state = 'new'
                            else:
                                state = 'expired'
                            values = {
                                'invoice_id': invoice.id,
                                'payment_id': payment.id,
                                'state': state,
                                'user_id': member.id,
                                'amount_base': total_credit,
                                'amount': amount,
                                'invoice_commission_percentage':
                                    invoice.commission_percentage,
                            }
                            commission_id = commission_obj.create(
                                cr, uid, values, context=context)
                            commission_ids.append(commission_id)
                        else:
                            for rule_line in rule_lines:
                                result = True
                                if rule_line.partner_category_id:
                                    if rule_line.partner_category_id not in \
                                            invoice.partner_id.category_id:
                                        result = result and False
                                if rule_line.pricelist_id:
                                    if invoice.pricelist_id:
                                        if not invoice.pricelist_id.id == \
                                                rule_line.pricelist_id.id:
                                            result = result and False
                                    else:
                                        result = result and False
                                if rule_line.payment_term_id:
                                    if invoice.payment_term:
                                        if not invoice.payment_term.id == \
                                                rule_line.payment_term_id:
                                            result = result and False
                                    else:
                                        result = result and False
                                if rule_line.max_discount > 0.0:
                                    if invoice.invoice_discount > \
                                            rule_line.max_discount:
                                        result = result and False
                                if rule_line.monthly_sales > 0.0:
                                    if total_sales < rule_line.monthly_sales:
                                        result = result and False
                                if result:
                                    if rule_line.commission_percentage and \
                                            total_credit:
                                        amount = total_credit * \
                                            rule_line.commission_percentage / \
                                            100
                                    else:
                                        amount = 0.0
                                    exp_days = relativedelta(
                                        days=rule.post_expiration_days)
                                    if invoice.date_due:
                                        inv_date = datetime.strptime(
                                            invoice.date_due, '%Y-%m-%d')
                                        payment_date = datetime.strptime(
                                            payment.date, '%Y-%m-%d')
                                        if payment_date > inv_date + exp_days:
                                            state = 'expired'
                                        else:
                                            state = 'new'
                                    else:
                                        state = 'expired'
                                    values = {
                                        'invoice_id': invoice.id,
                                        'payment_id': payment.id,
                                        'state': state,
                                        'user_id': member.id,
                                        'amount_base': total_credit,
                                        'amount': amount,
                                        'invoice_commission_percentage':
                                            rule_line.commission_percentage,
                                    }
                                    commission_id = commission_obj.create(
                                        cr, uid, values, context=context)
                                    commission_ids.append(commission_id)
                                    break
        return commission_ids

    def do_payment(self, cr, uid, ids, context=None):
        assert isinstance(ids, list)
        wizard = self.browse(cr, uid, ids[0], context=context)
        # Get the periods interval
        period_ids = self._get_interval_period(cr, uid, wizard.period_id,
                                               context=context)
        # Get all rules if there are not selected rules
        if not wizard.rule_ids:
            rule_obj = self.pool.get('sale.commission.rule')
            rule_ids = rule_obj.search(cr, uid, [], context=context)
            rules = rule_obj.browse(cr, uid, rule_ids, context=context)
        # Use the selected rules
        else:
            rules = wizard.rule_ids
        commission_ids = []
        for rule in rules:
            for member in rule.member_ids:
                # Invoices WITHOUT commission
                commission_ids += self._invoices_without_commission(
                    cr, uid, wizard, member, rule, period_ids, context=context)
                # Invoices WITH commission
                commission_ids += self._invoices_with_commission(
                    cr, uid, wizard, member, rule, period_ids, context=context)
        return {
            'name': _('Created Commissions'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.commission.commission',
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('id', 'in', commission_ids)],
            'context': context,
            'res_id': wizard.id,
        }

    _columns = {
        'period_id': fields.many2one('account.period', string='Period',
                                     required=True),
        'rule_ids': fields.many2many('sale.commission.rule',
                                     rel='sale_commission_wizard_rule_rel',
                                     string='Rules'),
    }
