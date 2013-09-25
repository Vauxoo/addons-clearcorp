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

class PersonnelActionType(osv.Model):
    _name = 'hr.personnelactions.actiontype'
    
    _rec_name = 'type'
    
    _columns = {
                'type': fields.char(string='Type', size=128, translate=True),
                }

class PersonnelActionConfiguration(osv.Model):
    _name = 'hr.personnelactions.config'
    
    _rec_name = 'key'
    
    _columns = {
                'key': fields.selection([('contract_creation', 'Contract Creation'),('contract_modification','Contract Modification'),('payroll_changes','Payroll Changes')], string='Key', required=True),
                'action_type_id': fields.many2one('hr.personnelactions.actiontype', string="Action Type", required=True),
                }
    
    _sql_constraints = [
                        ('unique_action_configuration_key','UNIQUE(key)','Keys cannot be duplicated'),
                        ]

class PersonnelAction(osv.Model):
    _name = 'hr.personnelactions.personnelaction'
    
    _columns = {
                'date': fields.datetime('Date', required=True),
                'title': fields.char(string='Title', size=128, required=True),
                'description': fields.text('Description'),
                'type_id': fields.many2one('hr.personnelactions.actiontype', string='Type', required=True, select=True),
                'employee_id': fields.many2one('hr.employee', string = 'Employee', required =True, select=True),
                }
    
class Contract(osv.Model):
    _inherit = 'hr.contract'
    
    def create(self, cr, uid, values, context=None):
        config_obj = self.pool.get('hr.personnelactions.config')
        config_id = config_obj.search(cr, uid, [('key','=','contract_creation')], context=context)
        if config_id:
            config = config_obj.browse(cr, uid, config_id[0], context=context)
            new_action = {
                          'date': fields.datetime.now(),
                          'title': _('Contract Creation'),
                          'description': _('A new contract has been created.'),
                          'type_id': config.action_type_id.id,
                          'employee_id': values['employee_id'],
                          }
            action_obj = self.pool.get('hr.personnelactions.personnelaction')
            action_obj.create(cr, uid, new_action, context=context)
        #TODO
        #else:
            #log or inform error couldn't create the action
        return super(Contract, self).create(cr,uid,values,context=context)
        
    
    def write(self, cr, uid, ids, values, context=None):
        config_obj = self.pool.get('hr.personnelactions.config')
        config_id = config_obj.search(cr, uid, [('key','=','contract_modification')], context=context)
        if config_id:
            config = config_obj.browse(cr, uid, config_id[0], context=context)
            contracts = self.browse(cr, uid, ids, context=context)
            for var_contract in contracts:
                str_values = ""
                for key in values.keys():
                    str_values += key + ': ' + str(values[key]) + '\n'
                str_message = _('Contract has been modified. Modifications are:') + '\n' + str_values
                new_action = {
                              'date': fields.datetime.now(),
                              'title': _('Contract Modifications'),
                              'description': str_message,
                              'type_id': config.action_type_id.id,
                              'employee_id': var_contract.employee_id.id,
                              }
                action_obj = self.pool.get('hr.personnelactions.personnelaction')
                action_obj.create(cr, uid, new_action, context=context)
        #TODO
        #else:
            #log or inform error couldn't create the action
        return super(Contract, self).write(cr,uid,ids,values,context=context)