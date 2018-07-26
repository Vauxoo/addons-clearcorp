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
from openerp.tools.translate import _
from odoo.exceptions import UserError

class personnelActionsType(models.Model):
    _name = 'hr.personnel.actions.type'
    _rec_name = 'type'

    type= fields.Char(string='Type', size=128, translate=True)

class personnelActionsConfiguration(models.Model):
    _name = 'hr.personnel.actions.configuration'
    _rec_name = 'key'

    key= fields.Selection(
            [('contract_wage', 'Contract Wage'),
             ('contract_duration', 'Contract Duration'),
             ('contract_payroll', 'Contract Payroll')],
            string='Key', required=True)
    action_type_id= fields.Many2one('hr.personnel.actions.type',
                                          string="Action Type",
                                          required=True)

    _sql_constraints = [
        ('unique_configuration_key', 'UNIQUE(key)',
         'Keys cannot be duplicated'),
    ]


class personnelActionsPersonnelAction(models.Model):
    _name = 'hr.personnel.actions.personnel.action'
    _rec_name = 'title'

    date=fields.Datetime('Date', required=True)
    sequence=fields.Char('Sequence', size=128, readonly=True)
    title=fields.Char(string='Title', size=128, required=True)
    description= fields.Text('Description')
    type_id=fields.Many2one('hr.personnel.actions.type',
                                   string='Type', required=True,
                                   index=True)
    employee_id= fields.Many2one('hr.employee',
                                       string='Employee',
                                       required=True, index=True)
    state=fields.Selection(
            [('draft', 'Draft'), ('approved', 'Approved'),
             ('cancelled', 'Cancelled')],
            string='Status', index=True,
            readonly=True, default='draft')

    def action_approved(self):
        sequence = self.env['ir.sequence'].get('personnel.actions')
        self.write({'state': 'approved', 'sequence': sequence})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

class hrContract(models.Model):
    _inherit = 'hr.contract'

    def _write_personnel_action(self,var_contract, configuration, message_new, message_old, new_value, old_value):
        if configuration:
            new_action = {
                'date': fields.datetime.now(),
                'title': _('Contract Modifications'),
                'description': message_new + (
                    ' %s. %s %s.' % (new_value, message_old, old_value)),
                'type_id': configuration.action_type_id.id,
                'employee_id': var_contract.employee_id.id,
                }
            action_obj = self.env['hr.personnel.actions.personnel.action']
            action= action_obj.create(new_action)
            action.action_approved()
        else:
            raise UserError(_('System cannot create the respective personnel action'))
    @api.multi
    def write(self,values):
        message_old = _('The old value was:')
        for var_contract in self:
            if 'wage' in values:
                configuration_obj = self.env['hr.personnel.actions.configuration']
                configuration_id = configuration_obj.search([('key', '=', 'contract_wage')])
                message_new = _(
                    'Wage has been modified. The new value for wage is:')
                var_contract._write_personnel_action(var_contract,
                    configuration_id, message_new, message_old, values['wage'],
                    var_contract.wage)

            if 'date_start' in values:
                configuration_obj = self.env['hr.personnel.actions.configuration']
                configuration_id = configuration_obj.search([('key', '=', 'contract_duration')])
                message_new = _(
                    'Duration has been modified. '
                    'The new value for start date is:')
                var_contract._write_personnel_action(var_contract, configuration_id, message_new, message_old,
                    values['date_start'], var_contract.date_start)
            if 'date_end' in values:
                configuration_obj = self.env['hr.personnel.actions.configuration']
                configuration_id = configuration_obj.search([('key', '=', 'contract_duration')])
                message_new = _(
                    'Duration has been modified. '
                    'The new value for end date is:')
                var_contract._write_personnel_action(var_contract,configuration_id, message_new, message_old,
                    values['date_end'], var_contract.date_end)

            if 'struct_id' in values:
                configuration_obj = self.env['hr.personnel.actions.configuration']
                configuration_id = configuration_obj.search([('key', '=', 'contract_payroll')])
                message_new = _(
                    'The salary structure has been modified. '
                    'The new value is:')
                struct_id_name = self.env['hr.payroll.structure'].browse(values['struct_id']).name
                var_contract._write_personnel_action(var_contract,configuration_id, message_new, message_old, struct_id_name,
                    var_contract.struct_id.name)

        return super(hrContract, self).write(values)


class hrEmployee(models.Model):
    _inherit = "hr.employee"

    personnel_action_ids=fields.One2many('hr.personnel.actions.personnel.action', 'employee_id',
            string="Personnel Actions")
    @api.multi
    def copy(self,default=None):
        if not default:
            default = {}
        default.update({
            'personnel_action_ids': []
        })
        return super(hrEmployee, self).copy(default=default)
