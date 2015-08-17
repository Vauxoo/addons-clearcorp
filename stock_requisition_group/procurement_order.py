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

from openerp import models, api


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.multi
    def name_get(self):
        result = []
        for procurement in self:
            result.append((procurement.id, '%s: %s' % (
                procurement.product_id.display_name or '',
                procurement.origin or '')))
        return result

    @api.model
    def _run(self, procurement):
        if procurement.rule_id and procurement.rule_id.action == 'buy' and \
                procurement.product_id.purchase_requisition:
            res = super(ProcurementOrder, self)._run(procurement)
            # Review if there is any created requisition
            requisition_obj = self.env['purchase.requisition']
            requisition = requisition_obj.search(
                [('group_id', '=', procurement.group_id.id),
                 ('state', '=', 'draft'),
                 ('id', '!=', procurement.requisition_id.id),
                 ('company_id', '=', procurement.company_id.id)], limit=1)
            if requisition:
                for line in procurement.requisition_id.line_ids:
                    line.procurement_id = procurement.id
                    line.requisition_id = requisition.id
                procurement.requisition_id.unlink()
                procurement.requisition_id = requisition.id
            else:
                # Assign the procurement group and
                # assign the sequence to the requisition
                procurement.requisition_id.write({
                    'group_id': procurement.group_id.id,
                    'name': procurement.origin,
                })
                for line in procurement.requisition_id.line_ids:
                    line.procurement_id = procurement.id
            return res
        else:
            return super(ProcurementOrder, self)._run(procurement)
