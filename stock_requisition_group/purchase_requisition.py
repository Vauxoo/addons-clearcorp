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

from openerp import models, fields, api


class PurchaseRequisition(models.Model):

    _inherit = 'purchase.requisition'

    @api.model
    def _prepare_purchase_order_line(
            self, requisition, requisition_line, purchase_id, supplier):
        res = super(PurchaseRequisition, self)._prepare_purchase_order_line(
            requisition, requisition_line, purchase_id, supplier)
        if requisition_line.procurement_id:
            res.update({
                'procurement_ids': [(4, requisition_line.procurement_id.id)]
            })
        return res

    group_id = fields.Many2one('procurement.group', string='Procurement Group')
    name = fields.Char(default='')


class PurchaseRequisitionLine(models.Model):

    _inherit = 'purchase.requisition.line'

    procurement_id = fields.Many2one(
        'procurement.order', string='Procurement Order')
