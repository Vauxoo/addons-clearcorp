# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields
from openerp.tools.translate import _


class personnelActionsType(osv.Model):
    _name = 'hr.personnel.actions.type'

    _rec_name = 'type'

    _columns = {'type': fields.char(string='Type', size=128, translate=True),
                }


class personnelActionsConfiguration(osv.Model):
    _name = 'hr.personnel.actions.configuration'

    _rec_name = 'key'

    _columns = {
        'key': fields.selection(
            [('contract_wage', 'Contract Wage'),
             ('contract_duration', 'Contract Duration'),
             ('contract_payroll', 'Contract Payroll'), ],
            string='Key', required=True),
        'action_type_id': fields.many2one('hr.personnel.actions.type',
                                          string="Action Type",
                                          required=True),
    }

    _sql_constraints = [
        ('unique_configuration_key', 'UNIQUE(key)',
         'Keys cannot be duplicated'),
    ]


class personnelActionsPersonnelAction(osv.Model):
    _name = 'hr.personnel.actions.personnel.action'

    _rec_name = 'title'

    _columns = {
        'date': fields.datetime('Date', required=True),
        'sequence': fields.char('Sequence', size=128, readonly=True),
        'title': fields.char(string='Title', size=128, required=True),
        'description': fields.text('Description'),
        'type_id': fields.many2one('hr.personnel.actions.type',
                                   string='Type', required=True,
                                   select=True),
        'employee_id': fields.many2one('hr.employee',
                                       string='Employee',
                                       required=True, select=True),
        'state': fields.selection(
            [('draft', 'Draft'), ('approved', 'Approved'),
             ('cancelled', 'Cancelled')],
            string='Status', index=True,
            readonly=True, default='draft')
    }

    def action_approved(self, cr, uid, ids, context=None):
        sequence = self.pool.get('ir.sequence').get(
            cr, uid, 'personnel.actions')
        self.write(cr, uid, ids, {'state': 'approved', 'sequence': sequence},
                   context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancelled'},
                   context=context)


class hrContract(osv.Model):
    _inherit = 'hr.contract'

    def _write_personnel_action(
            self, cr, uid, ids, context, var_contract, configuration_obj,
            configuration_id, message_new, message_old, new_value, old_value):
        if configuration_id:
            configuration = configuration_obj.browse(
                cr, uid, configuration_id[0], context=context)
            new_action = {
                'date': fields.datetime.now(),
                'title': _('Contract Modifications'),
                'description': message_new + (
                    ' %s. %s %s.' % (new_value, message_old, old_value)),
                'type_id': configuration.action_type_id.id,
                'employee_id': var_contract.employee_id.id,
                }
            action_obj = self.pool.get('hr.personnel.actions.personnel.action')
            action_id = action_obj.create(cr, uid, new_action, context=context)
            action_obj.action_approved(cr, uid, action_id, context=context)
        else:
            raise osv.except_osv(_(
                'Personnel Actions Error'),
                _('System cannot create the respective personnel action'))

    def write(self, cr, uid, ids, values, context=None):
        contracts = self.browse(cr, uid, ids, context=context)
        message_old = _('The old value was:')
        for var_contract in contracts:
            if 'wage' in values:
                configuration_obj = self.pool.get(
                    'hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(
                    cr, uid, [('key', '=', 'contract_wage')], context=context)
                message_new = _(
                    'Wage has been modified. The new value for wage is:')
                self._write_personnel_action(
                    cr, uid, ids, context, var_contract, configuration_obj,
                    configuration_id, message_new, message_old, values['wage'],
                    var_contract.wage)

            if 'date_start' in values:
                configuration_obj = self.pool.get(
                    'hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(
                    cr, uid, [('key', '=', 'contract_duration')],
                    context=context)
                message_new = _(
                    'Duration has been modified. '
                    'The new value for start date is:')
                self._write_personnel_action(
                    cr, uid, ids, context, var_contract, configuration_obj,
                    configuration_id, message_new, message_old,
                    values['date_start'], var_contract.date_start)

            if 'date_end' in values:
                configuration_obj = self.pool.get(
                    'hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(
                    cr, uid, [('key', '=', 'contract_duration')],
                    context=context)
                message_new = _(
                    'Duration has been modified. '
                    'The new value for end date is:')
                self._write_personnel_action(
                    cr, uid, ids, context, var_contract, configuration_obj,
                    configuration_id, message_new, message_old,
                    values['date_end'], var_contract.date_end)

            if 'struct_id' in values:
                configuration_obj = self.pool.get(
                    'hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(
                    cr, uid, [('key', '=', 'contract_payroll')],
                    context=context)
                message_new = _(
                    'The salary structure has been modified. '
                    'The new value is:')
                struct_id_name = self.pool.get('hr.payroll.structure').browse(
                    cr, uid, values['struct_id'], context=context).name
                self._write_personnel_action(
                    cr, uid, ids, context, var_contract, configuration_obj,
                    configuration_id, message_new, message_old, struct_id_name,
                    var_contract.struct_id.name)

        return super(hrContract, self).write(cr, uid, ids, values,
                                             context=context)


class hrEmployee(osv.Model):
    _inherit = "hr.employee"

    _columns = {
        'personnel_action_ids': fields.one2many(
            'hr.personnel.actions.personnel.action', 'employee_id',
            string="Personnel Actions")
    }

    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'personnel_action_ids': []
        })
        return super(hrEmployee, self).copy(cr, uid, id, default=default,
                                            context=context)
