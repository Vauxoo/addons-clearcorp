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

from osv import orm, osv, fields
from tools.translate import _

class PurchaseOrder(orm.Model):

    _inherit = 'purchase.order'
        
    def create(self, cr, uid, vals, context=None):
        purchase_product_ids = []
        if 'order_line' in vals: 
            order_lines = vals['order_line']
            for line in order_lines:
                line = line[2] #to extract the new vals of the line
                if 'product_id' in line and line['product_id'] not in purchase_product_ids:
                    purchase_product_ids.append(line['product_id'])
                else:
                    raise osv.except_osv(_('Error !'), _('This purchase order have lines with same products!'))
        return super(PurchaseOrder, self).create(cr, uid, vals, context=context)
        
    
    def write(self, cr, uid, ids, vals, context=None):
        purchase_product_ids = []
        if 'order_line' in vals: 
            order_lines = vals['order_line']
            purchase_orders = self.browse(cr, uid, ids, context)
            for purchase_order in purchase_orders:
                for old_line in purchase_order.order_line:
                    if old_line.product_id.id not in purchase_product_ids:
                        purchase_product_ids.append(old_line.product_id.id)
                    else:
                        raise osv.except_osv(_('Error !'), _('This purchase order have lines with same products!'))
                for line in order_lines:
                    new_line = line[2] #to extract the new vals of the line
                    if new_line and 'product_id' in new_line.keys(): 
                        if 'product_id' in new_line and new_line['product_id'] not in purchase_product_ids:
                            purchase_product_ids.append(new_line['product_id'])
                        else:
                            raise osv.except_osv(_('Error !'), _('This purchase order have lines with same products!'))
        return super(PurchaseOrder, self).write(cr, uid, ids, vals, context=context)
