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

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    purchase_date=fields.Date('Purchase order date')
    
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def invoice_validate(self):
        self.env['sale.order'].search
        for invoice in self:
            for sale_order in invoice.order_ids:
                if sale_order.origin:
                    if sale_order.purchase_date:
                        if sale_order.purchase_date>self.date_invoice:
                            raise Warning(_('Purchase order date is greater than date to invoice'))
                    else:
                        raise Warning(_('No assigned date to purchase order of customer'))
        return super(AccountInvoice,self).invoice_validate()
     
    order_ids= fields.Many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id','order_id', 'Sales Order', readonly=True, copy=False, help="This is the list of sales orders that have been generated for this invoice.")