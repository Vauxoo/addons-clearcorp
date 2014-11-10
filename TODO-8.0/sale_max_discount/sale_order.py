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
import openerp.addons.decimal_precision as dp

class SaleOrder(osv.Model):

    _inherit = 'sale.order'

    def action_button_confirm(self, cr, uid, ids, context=None):
        if not self.pool.get('res.users').has_group(cr, uid,
        'sale_max_discount.group_sale_max_discount'):
            for sale_order in self.browse(cr, uid, ids, context=context):
                pricelist = sale_order.pricelist_id
                if pricelist and pricelist.discount_active:
                    max_discount = [pricelist.max_discount]
                else:
                    max_discount = []
                for line in sale_order.order_line:
                    line_discount = max_discount
                    if line.product_id:
                        if line.product_id.categ_id.discount_active:
                            line_discount.append(line.product_id.categ_id.max_discount)
                    if line_discount:
                        lower_discount = min(line_discount)
                        if line.discount and line.discount > lower_discount:
                            raise osv.except_osv(_('Discount Error'),
                                _('The maximum discount for %s is %s.') %(line.name, lower_discount))
                    else:
                        #Get company for user currently logged
                        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
                        if company.limit_discount_active:
                            max_company_discount = company.limit_discount_max_discount 
                            if line.discount > max_company_discount:
                                raise osv.except_osv(_('Discount Error'), _('The discount for %s exceeds the'
                                    ' company\'s discount limit.') % line.name)
        return super(SaleOrder, self).action_button_confirm(cr, uid, ids, context=context)