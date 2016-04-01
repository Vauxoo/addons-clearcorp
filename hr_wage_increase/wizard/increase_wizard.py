# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields
from openerp.tools.translate import _


class WageIncreaseWizard(osv.TransientModel):

    _name = 'hr.wage.increase.increase.wizard'

    def _check_amount_percentage(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.increase_type == 'percentage':
                if wizard.amount_percentage <= 0.0 or\
                        wizard.amount_percentage > 100:
                    return False
        return True

    def _check_amount_fixed(self, cr, uid, ids, context=None):
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.increase_type == 'fixed_amount':
                if wizard.amount_fixed <= 0.0:
                    return False
        return True

    def process_wage_increase(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids and ids[0]
        wizard = self.browse(cr, uid, ids, context=context)
        try:
            contract_ids = []
            for contract in wizard.contract_ids:
                new_wage = None
                if wizard.increase_type == 'percentage':
                    new_wage = contract.wage +\
                        (contract.wage * wizard.amount_percentage / 100)
                else:
                    new_wage = contract.wage + wizard.amount_fixed
                contract.write({'wage': new_wage})
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
            raise osv.except_osv(
                _('Error Processing Contracts'),
                _('An error occurred while processing the contracts'))

    _columns = {
        'increase_type': fields.selection(
            [('percentage', 'Percentage (%)'),
             ('fixed_amount', 'Fixed Amount')
             ],
            string='Increase Type', required=True),
        'amount_percentage': fields.float('Increase Percentage'),
        'amount_fixed': fields.float('Amount', digits=(16, 2)),
        'contract_ids': fields.many2many('hr.contract', string='Contracts',
                                         required=True),
    }

    _defaults = {
        'increase_type': 'fixed_amount',
    }

    _constraints = [
        (_check_amount_percentage,
         'Value must be greater than 0 and lower or equal than 100.',
         ['amount_percentage']),
        (_check_amount_fixed, 'Value must be greater than 0.',
         ['amount_fixed'])
    ]
