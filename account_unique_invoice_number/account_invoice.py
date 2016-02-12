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

from openerp import models, api, _
from openerp.exceptions import Warning


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def create(self, vals):
        if 'supplier_invoice_number' in vals and \
                vals['supplier_invoice_number'] and \
                vals['supplier_invoice_number'] != '':
            qty = self.search_count([('supplier_invoice_number', '=',
                                     vals['supplier_invoice_number']),
                                    ('partner_id', '=', vals['partner_id'])])
            if qty >= 1:
                raise Warning(_('Duplicated Supplier Invoice Number'))

        return super(account_invoice, self).create(vals)

    @api.multi
    def write(self, vals):
        for invoice in self:
            if 'supplier_invoice_number' in vals and \
                    vals['supplier_invoice_number'] and \
                    vals['supplier_invoice_number'] != '':
                partner_id = 'partner_id' in vals and \
                    vals['partner_id'] or invoice.partner_id

                qty = self.search_count([('supplier_invoice_number', '=',
                                        vals['supplier_invoice_number']),
                                        ('partner_id', '=', partner_id.id)])
                if qty >= 1 or len(self._ids) > 1:
                    raise Warning(_('Duplicated Supplier Invoice Number'))
        return super(account_invoice, self).write(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['supplier_invoice_number'] = ""
        return super(account_invoice, self).copy(default=default)
