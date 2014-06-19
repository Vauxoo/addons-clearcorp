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

class personnelActionsType(osv.Model):
    _name = 'hr.personnel.actions.type'
    
    _rec_name = 'type'
    
    _columns = {
                'type': fields.char(string='Type', size=128, translate=True),
                }

class personnelActionsConfiguration(osv.Model):
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

class personnelActionsPersonnelAction(osv.Model):
    _name = 'hr.personnel.actions.personnel.action'
    
    _rec_name = 'title'
    
    def create(self, cr ,uid, values, context=None):
        values['sequence'] = self.pool.get('ir.sequence').get(cr, uid, 'personnel.actions')
        return super(personnelActionsPersonnelAction,self).create(cr, uid, values, context=context)
    
    _columns = {
                'date': fields.datetime('Date', required=True),
                'sequence': fields.char('Sequence', size=128, readonly=True),
                'title': fields.char(string='Title', size=128, required=True),
                'description': fields.text('Description'),
                'type_id': fields.many2one('hr.personnel.actions.type', string='Type', required=True, select=True),
                'employee_id': fields.many2one('hr.employee', string = 'Employee', required =True, select=True),
                }
    
class hrContract(osv.Model):
    _inherit = 'hr.contract'
    
    def _write_personnel_action(self, cr, uid, ids, context, var_contract, configuration_obj, configuration_id, message_new, message_old, new_value, old_value):
        if configuration_id:
            configuration = configuration_obj.browse(cr, uid, configuration_id[0], context=context)
            contracts = self.browse(cr, uid, ids, context=context)
            new_action = {
                          'date': fields.datetime.now(),
                          'title': _('Contract Modifications'),
                          'description': message_new + (' %s. %s %s.' % (new_value, message_old, old_value)),
                          'type_id': configuration.action_type_id.id,
                          'employee_id': var_contract.employee_id.id,
                          }
            action_obj = self.pool.get('hr.personnel.actions.personnel.action')
            action_obj.create(cr, uid, new_action, context=context)
        else:
            raise osv.except_osv(_('Personnel Actions Error'), _('System cannot create the respective personnel action'))
    
    def write(self, cr, uid, ids, values, context=None):
        contracts = self.browse(cr, uid, ids, context=context)
        message_old = _('The old value was:')
        for var_contract in contracts:
            if 'wage' in values:
                configuration_obj = self.pool.get('hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_wage')], context=context)
                message_new = _('Wage has been modified. The new value for wage is:')
                self._write_personnel_action(cr,uid,ids,context,var_contract,configuration_obj,configuration_id,message_new,message_old,values['wage'],var_contract.wage)
                
            if 'date_start' in values:
                configuration_obj = self.pool.get('hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_duration')], context=context)
                message_new = _('Duration has been modified. The new value for start date is:')
                self._write_personnel_action(cr,uid,ids,context,var_contract,configuration_obj,configuration_id,message_new,message_old,values['date_start'],var_contract.date_start)
                
            if 'date_end' in values:
                configuration_obj = self.pool.get('hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_duration')], context=context)
                message_new = _('Duration has been modified. The new value for end date is:')
                self._write_personnel_action(cr,uid,ids,context,var_contract,configuration_obj,configuration_id,message_new,message_old,values['date_end'],var_contract.date_end)
                
            if 'struct_id' in values:
                configuration_obj = self.pool.get('hr.personnel.actions.configuration')
                configuration_id = configuration_obj.search(cr, uid, [('key','=','contract_payroll')], context=context)
                message_new = _('The salary structure has been modified. The new value is:')
                struct_id_name = self.pool.get('hr.payroll.structure').browse(cr, uid, values['struct_id'], context=context).name
                self._write_personnel_action(cr,uid,ids,context,var_contract,configuration_obj,configuration_id,message_new,message_old,struct_id_name,var_contract.struct_id.name)
                
        return super(hrContract, self).write(cr,uid,ids,values,context=context)
    
class hrEmployee(osv.Model):
    _inherit = "hr.employee"
    
    _columns = {
                'personnel_action_ids': fields.one2many('hr.personnel.actions.personnel.action', 'employee_id', string="Personnel Actions")
                }