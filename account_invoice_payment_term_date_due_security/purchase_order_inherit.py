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

class purchaseOrderinherit(orm.Model):
    
     _inherit = 'purchase.order'
     
     def _get_payment_term(self, cr, uid, ids, fields, arg, context=None):
        res = {}        
        for purchase in self.browse(cr, uid, ids, context=context):
            if purchase.payment_term_id:
                res[purchase.id] = purchase.payment_term_id.id
        return res

     _columns = {
        'payment_term_visible': fields.function(_get_payment_term, type='many2one', relation='account.payment.term', 
            store={'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['payment_term_id'], 10),}, string="Payment Term",),
       }
     
     def onchange_partner_id(self, cr, uid, ids, partner_id):       
        res = super(purchaseOrderinherit, self).onchange_partner_id(cr, uid, ids, partner_id)
                
        if 'payment_term_id' in res['value'].keys():
            res['value'].update({'payment_term_visible': res['value']['payment_term_id']})
                
        return res  
    
     def onchange_payment_term_visible(self, cr, uid, ids, payment_term_visible):
        res = {}
        res['value'] = {}
        
        if payment_term_visible:
            res['value'].update({'payment_term_id':payment_term_visible})
             
        return res          
     