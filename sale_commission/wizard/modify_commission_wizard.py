# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp.exceptions import ValidationError
from openerp.models import _


class ModifyCommission(models.TransientModel):

    _name = 'sale.commission.modify.wizard'

    def commission_pay(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        commission_obj = self.pool.get('sale.commission.commission')
        for com in commission_obj.browse(cr, uid, active_ids, context=context):
            if com.state != 'new':
                raise ValidationError(
                    _('Selected commission(s) cannot be paid as they are '
                      'not in "New" state.'))
            com.write({'state': 'paid'})
        return {'type': 'ir.actions.act_window_close'}
