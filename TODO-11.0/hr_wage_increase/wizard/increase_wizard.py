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

from odoo import tools,models, fields, api,_
from openerp.tools.translate import _
from odoo.exceptions import UserError

class WageIncreaseWizard(models.TransientModel):
    _name = 'hr.wage.increase.increase.wizard'
    @api.one
    @api.constrains('increase_type','amount_percentage')
    def _check_amount_percentage(self):
        for wizard in self:
            if wizard.increase_type == 'percentage':
                if wizard.amount_percentage <= 0.0 or wizard.amount_percentage > 100:
                    raise Warning(_('Value must be greater than 0 and lower or equal than 100.'))
        return True
    @api.one
    @api.constrains('increase_type','amount_fixed')
    def _check_amount_fixed(self):
        for wizard in self:
            if wizard.increase_type == 'fixed_amount':
                if wizard.amount_fixed <= 0.0:
                    raise Warning(_('Value must be greater than 0.'))
        return True

    def process_wage_increase(self):
        try:
            contract_ids = []
            for contract in self.contract_ids:
                new_wage = None
                if self.increase_type == 'percentage':
                    new_wage = contract.wage + (contract.wage * self.amount_percentage / 100)
                else:
                    new_wage = contract.wage + self.amount_fixed
                contract.write({'wage': new_wage})
                contract_ids.append(contract.id)
            return {
                'name': _('Updated contracts'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.contract',
                'view_id': False,
                'domain': "[('id','in',%s)]" % contract_ids,
                'type': 'ir.actions.act_window',
            }
        except:
            raise Warning(_('An error occurred while processing the contracts'))

    increase_type= fields.Selection([('percentage','Percentage (%)'),('fixed_amount','Fixed Amount')],default='fixed_amount',string='Increase Type', required=True)
    amount_percentage=fields.Float('Increase Percentage')
    amount_fixed= fields.Float('Amount', digits=(16,2))
    contract_ids= fields.Many2many('hr.contract', string='Contracts', required=True)