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
from osv import fields, osv

class ccorp_purchase_order_sequence(osv.osv):
    _inherit = 'purchase.order'
    
    _columns ={
        'name': fields.char('Order Reference', size=64, 
            select=True, help="unique number of the purchase order,computed automatically when the purchase order is created"),
        }
    _defaults = {
        'name': '',
        }
    
    def create(self, cr, uid, vals, context=None): 
        if not 'name' in vals:
            sequence  = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order', context=context) or '/'
            vals['name'] = sequence
        result = super(ccorp_purchase_order_sequence, self).create(cr, uid, vals, context=context)
        return result

