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
from tools.translate import _

class type(osv.Model):
    _name = 'hr.personnel.actions.type'
    
    _rec_name = 'type'
    
    _columns = {
                'type': fields.char(string='Type', size=128, translate=True),
                }

class configuration(osv.Model):
    _name = 'hr.personnel.actions.configuration'
    
    _rec_name = 'key'
    
    _columns = {
                'key': fields.selection([
                                         ('contract_wage','Contract Wage'),
                                         ('contract_duration','Contract Duration'),
                                         ('contract_payroll','Contract Payroll'),
                                         ], string='Key', required=True),
                'action_type_id': fields.many2one('hr.personnel.actions.type', string="Action Type", required=True),
                }
    
    _sql_constraints = [
                        ('unique_configuration_key','UNIQUE(key)','Keys cannot be duplicated'),
                        ]

class personnelAction(osv.Model):
    _name = 'hr.personnel.actions.personnel.action'
    
    _columns = {
                'date': fields.datetime('Date', required=True),
                'title': fields.char(string='Title', size=128, required=True),
                'description': fields.text('Description'),
                'type_id': fields.many2one('hr.personnel.actions.type', string='Type', required=True, select=True),
                'employee_id': fields.many2one('hr.employee', string = 'Employee', required =True, select=True),
                }
    
class contract(osv.Model):
    _inherit = 'hr.contract'
    
    def write(self, cr, uid, ids, values, context=None):
        if 'wage' in values:
            configuration_obj = self.pool.get('hr.personnel.actions.configuration')
            configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_wage')], context=context)
            if configuration_id:
                configuration = configuration_obj.browse(cr, uid, configuration_id[0], context=context)
                contracts = self.browse(cr, uid, ids, context=context)
                for var_contract in contracts:
                    new_action = {
                                  'date': fields.datetime.now(),
                                  'title': _('Contract Modifications'),
                                  'description': _('Wage has been modified. The new value for wage is:') +
                                  (' %s. ' % values['wage']) + _('The old value was:') +
                                  (' %s.' % var_contract.wage),
                                  'type_id': configuration.action_type_id.id,
                                  'employee_id': var_contract.employee_id.id,
                                  }
                    action_obj = self.pool.get('hr.personnel.actions.personnel.action')
                    action_obj.create(cr, uid, new_action, context=context)
            #TODO
            #else:
                #log or inform error couldn't create the action
        if 'date_start' in values:
            configuration_obj = self.pool.get('hr.personnel.actions.configuration')
            configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_duration')], context=context)
            if configuration_id:
                configuration = configuration_obj.browse(cr, uid, configuration_id[0], context=context)
                contracts = self.browse(cr, uid, ids, context=context)
                for var_contract in contracts:
                    new_action = {
                                  'date': fields.datetime.now(),
                                  'title': _('Contract Modifications'),
                                  'description': _('Duration has been modified. The new value for start date is:') +
                                  (' %s. ' %values['date_start']) + _('The old value was:') +
                                  (' %s.' % var_contract.date_start),
                                  'type_id': configuration.action_type_id.id,
                                  'employee_id': var_contract.employee_id.id,
                                  }
                    action_obj = self.pool.get('hr.personnel.actions.personnel.action')
                    action_obj.create(cr, uid, new_action, context=context)
            #TODO
            #else:
                #log or inform error couldn't create the action
        if 'date_end' in values:
            configuration_obj = self.pool.get('hr.personnel.actions.configuration')
            configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_duration')], context=context)
            if configuration_id:
                configuration = configuration_obj.browse(cr, uid, configuration_id[0], context=context)
                contracts = self.browse(cr, uid, ids, context=context)
                for var_contract in contracts:
                    new_action = {
                                  'date': fields.datetime.now(),
                                  'title': _('Contract Modifications'),
                                  'description': _('Duration has been modified. The new value for end date is:') +
                                  (' %s. ' %values['date_end']) + _('The old value was:') +
                                  (' %s.' % var_contract.date_end),
                                  'type_id': configuration.action_type_id.id,
                                  'employee_id': var_contract.employee_id.id,
                                  }
                    action_obj = self.pool.get('hr.personnel.actions.personnel.action')
                    action_obj.create(cr, uid, new_action, context=context)
            #TODO
            #else:
                #log or inform error couldn't create the action
        if 'struct_id' in values:
            configuration_obj = self.pool.get('hr.personnel.actions.configuration')
            configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_payroll')], context=context)
            if configuration_id:
                configuration = configuration_obj.browse(cr, uid, configuration_id[0], context=context)
                contracts = self.browse(cr, uid, ids, context=context)
                for var_contract in contracts:
                    struct_id_name = self.pool.get('hr.payroll.structure').browse(cr, uid, values['struct_id'], context=context).name
                    new_action = {
                                  'date': fields.datetime.now(),
                                  'title': _('Contract Modifications'),
                                  'description': _('The salary structure has been modified. The new value is:') +
                                  (' %s. ' % struct_id_name) + _('The old value was:') +
                                  (' %s.' % var_contract.struct_id.name),
                                  'type_id': configuration.action_type_id.id,
                                  'employee_id': var_contract.employee_id.id,
                                  }
                    action_obj = self.pool.get('hr.personnel.actions.personnel.action')
                    action_obj.create(cr, uid, new_action, context=context)
            #TODO
            #else:
                #log or inform error couldn't create the action
        return super(contract, self).write(cr,uid,ids,values,context=context)