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

class WageIncreaseWizard(osv.TransientModel):

    _name = 'hr.wage.increase.increase.wizard'

    def _check_amount_percentage(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.increase_type == 'percentage':
                if wizard.amount_percentage <= 0.0 or wizard.amount_percentage > 100:
                    return False
        return True
    
    def _check_amount_fixed(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.increase_type == 'fixed_amount':
                if wizard.amount_fixed <= 0.0:
                    return False
        return True

    def process_wage_increase(self, cr, uid, ids, context=None):
        if isinstance(ids,list):
            ids = ids and ids[0]
        wizard = self.browse(cr, uid, ids, context=context)
        try:
            contract_ids = []
            for contract in wizard.contract_ids:
                new_wage = None
                if wizard.increase_type == 'percentage':
                    new_wage = contract.wage + (contract.wage * wizard.amount_percentage / 100)
                else:
                    new_wage = contract.wage + wizard.amount_fixed
                contract.write({'wage': new_wage}, context=context)
                contract_ids.append(contract.id)
            return {
                'name': _('Updated contracts'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'hr.contract',
                'view_id': False,
                'context': context, 
                'domain': "[('id','in',%s)]" % contract_ids,
                'type': 'ir.actions.act_window',
            }
        except:
            raise osv.except_osv(_('Error Processing Contracts'),
                                 _('An error occurred while processing the contracts'))

    _columns = {
        'increase_type': fields.selection([('percentage','Percentage (%)'),('fixed_amount','Fixed Amount')],
            string='Increase Type', required=True),
        'amount_percentage': fields.float('Increase Percentage'),
        'amount_fixed': fields.float('Amount', digits=(16,2)),
        'contract_ids': fields.many2many('hr.contract', string='Contracts', required=True),
    }

    _defaults = {
        'increase_type': 'fixed_amount',
    }

    _constraints = [(_check_amount_percentage,
                     'Value must be greater than 0 and lower or equal than 100.',
                     ['Increase Percentage']),
                    (_check_amount_fixed,
                     'Value must be greater than 0.',
                     ['Amount'])]