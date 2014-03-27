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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class purchaseOrderinherit(orm.Model):

    _inherit = 'purchase.order'
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        
        #Original method does comprobation if purchase order  
        #have not lines.
        for po in self.browse(cr, uid, ids, context=context):
            if po.order_line:
                 for line in po.order_line:
                     if not line.product_id:
                         raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order line without product'))
        
        return super(purchaseOrderinherit, self).wkf_confirm_order(cr, uid, ids, context=context)