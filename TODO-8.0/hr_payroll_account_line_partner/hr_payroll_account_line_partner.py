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

class SalaryRule(osv.Model):

    _RULE_TYPES = [
                   ('partner', 'Partner'),
                   ('employee', 'Employee'),
                   ]

    _inherit = 'hr.salary.rule'

    _columns = {
                'rule_type_credit': fields.selection(_RULE_TYPES, string='Credit Rule Type'),
                'rule_type_debit': fields.selection(_RULE_TYPES, string='Debit Rule Type'),
                'res_partner_credit': fields.many2one('res.partner', string='Credit Partner'),
                'res_partner_debit': fields.many2one('res.partner', string='Debit Partner'),
                }

    _defaults = {
                 'rule_type_credit': 'employee',
                 'rule_type_debit': 'employee',
                 }

class PaySlip(osv.Model):

    _inherit = 'hr.payslip'

    def process_sheet(self, cr, uid, ids, context=None):
        res = super(PaySlip, self).process_sheet(cr, uid, ids, context=context)
        for payslip in self.browse(cr, uid, ids, context=context):
            for line in payslip.line_ids:
                if line.salary_rule_id:
                    # Check is salary rule has debit
                    if line.salary_rule_id.account_debit:
                        # Check if rule has rule_type_debit
                        if line.salary_rule_id.rule_type_debit:
                            move_line_obj = self.pool.get('account.move.line')
                            # Check the rule_type if partner
                            if line.salary_rule_id.rule_type_debit == 'partner':
                                move_line_ids = move_line_obj.search(cr, uid,
                                [('move_id','=',payslip.move_id.id), ('debit','=',line.total),
                                 ('account_id','=',line.salary_rule_id.account_debit.id)], context=context)
                                if move_line_ids:
                                    move_line_obj.write(cr, uid, move_line_ids[0],
                                    {'partner_id': line.salary_rule_id.res_partner_debit.id}, context=context)
                            # Rule type is employee
                            else:
                                move_line_ids = move_line_obj.search(cr, uid,
                                [('move_id','=',payslip.move_id.id), ('debit','=',line.total),
                                 ('account_id','=',line.salary_rule_id.account_debit.id)], context=context)
                                if move_line_ids:
                                    move_line_obj.write(cr, uid, move_line_ids[0],
                                    {'partner_id': payslip.employee_id.address_home_id.id}, context=context)
                    # Credit check if salary rule has credit
                    if line.salary_rule_id.account_credit:
                        # Check if rule has rule_type credit
                        if line.salary_rule_id.rule_type_credit:
                            move_line_obj = self.pool.get('account.move.line')
                            # Check if rule_type is partner
                            if line.salary_rule_id.rule_type_credit == 'partner':
                                move_line_ids = move_line_obj.search(cr, uid,
                                    [('move_id','=',payslip.move_id.id), ('credit','=',line.total),
                                     ('account_id','=',line.salary_rule_id.account_credit.id)], context=context)
                                if move_line_ids:
                                    move_line_obj.write(cr, uid, move_line_ids[0],
                                    {'partner_id': line.salary_rule_id.res_partner_credit.id}, context=context)
                            # Rule type is employee
                            else:
                                move_line_ids = move_line_obj.search(cr, uid,
                                    [('move_id','=',payslip.move_id.id), ('credit','=',line.total),
                                     ('account_id','=',line.salary_rule_id.account_credit.id)], context=context)
                                if move_line_ids:
                                    move_line_obj.write(cr, uid, move_line_ids[0],
                                    {'partner_id': payslip.employee_id.address_home_id.id}, context=context)
        return res
