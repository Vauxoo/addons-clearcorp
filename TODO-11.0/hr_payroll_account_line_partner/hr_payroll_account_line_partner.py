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

from odoo import models, fields, api, _

class SalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _RULE_TYPES = [
                   ('partner', 'Partner'),
                   ('employee', 'Employee'),
                   ]
    rule_type_credit=fields.Selection(_RULE_TYPES, string='Credit Rule Type',default='employee')
    rule_type_debit=fields.Selection(_RULE_TYPES, string='Debit Rule Type',default='employee')
    res_partner_credit=fields.Many2one('res.partner', string='Credit Partner')
    res_partner_debit=fields.Many2one('res.partner', string='Debit Partner')

class PaySlip(models.Model):
    _inherit = 'hr.payslip'
    @api.multi
    def action_payslip_done(self):
        res = super(PaySlip, self).action_payslip_done()
        for payslip in self:
            for line in payslip.line_ids:
                if line.salary_rule_id:
                    # Check is salary rule has debit
                    if line.salary_rule_id.account_debit:
                        # Check if rule has rule_type_debit
                        if line.salary_rule_id.rule_type_debit:
                            move_line_obj = self.env['account.move.line']
                            # Check the rule_type if partner
                            if line.salary_rule_id.rule_type_debit == 'partner':
                                move_line_ids = move_line_obj.search([('move_id','=',payslip.move_id.id), ('debit','=',line.total),
                                 ('account_id','=',line.salary_rule_id.account_debit.id)])
                                if move_line_ids:
                                    move_line_ids[0].write({'partner_id': line.salary_rule_id.res_partner_debit.id})
                            # Rule type is employee
                            else:
                                move_line_ids = move_line_obj.search([('move_id','=',payslip.move_id.id), ('debit','=',line.total),
                                 ('account_id','=',line.salary_rule_id.account_debit.id)])
                                if move_line_ids:
                                    move_line_ids[0].write({'partner_id': payslip.employee_id.address_home_id.id})
                    # Credit check if salary rule has credit
                    if line.salary_rule_id.account_credit:
                        # Check if rule has rule_type credit
                        if line.salary_rule_id.rule_type_credit:
                            move_line_obj = self.env['account.move.line']
                            # Check if rule_type is partner
                            if line.salary_rule_id.rule_type_credit == 'partner':
                                move_line_ids = move_line_obj.search([('move_id','=',payslip.move_id.id), ('credit','=',line.total),
                                     ('account_id','=',line.salary_rule_id.account_credit.id)])
                                if move_line_ids:
                                    move_line_ids[0].write({'partner_id': line.salary_rule_id.res_partner_credit.id})
                            # Rule type is employee
                            else:
                                move_line_ids = move_line_obj.search([('move_id','=',payslip.move_id.id), ('credit','=',line.total),
                                     ('account_id','=',line.salary_rule_id.account_credit.id)])
                                if move_line_ids:
                                    move_line_ids[0].write({'partner_id': payslip.employee_id.address_home_id.id})
        return res
