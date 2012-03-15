# -*- encoding: utf-8 -*-
##############################################################################
#
#    purchase_change_pricelist.py
#    purchase_change_pricelist
#    First author: Mag Guevara <mag.guevara@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2011-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
#    
#    Redistribution and use in source and binary forms, with or without modification, are
#    permitted provided that the following conditions are met:
#    
#       1. Redistributions of source code must retain the above copyright notice, this list of
#          conditions and the following disclaimer.
#    
#       2. Redistributions in binary form must reproduce the above copyright notice, this list
#          of conditions and the following disclaimer in the documentation and/or other materials
#          provided with the distribution.
#    
#    THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ``AS IS'' AND ANY EXPRESS OR IMPLIED
#    WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR
#    CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#    NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#    ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#    
#    The views and conclusions contained in the software and documentation are those of the
#    authors and should not be interpreted as representing official policies, either expressed
#    or implied, of ClearCorp S.A..
#    
##############################################################################
from osv import osv, fields
from tools import debug
from tools.translate import _

class purchase_change_pricelist(osv.osv_memory):
	_name = 'purchase.change.pricelist'
	
	_columns = {
		'pricelist_id': fields.many2one('product.pricelist', 'Change to', required=True, help="Select a pricelist to apply on the purchase order"),
	}
	
	def view_init(self, cr , uid , fields_list, context=None):
		obj_inv = self.pool.get('purchase.order')
		if context is None:
			context = {}
		if context.get('active_id',False):
			if obj_inv.browse(cr, uid, context['active_id']).state != 'draft':
				raise osv.except_osv(_('Error'), _('You can only change pricelist for Draft orders !'))
			pass
	
	def change_currency(self, cr, uid, ids, context=None):
		obj_po = self.pool.get('purchase.order')
		obj_po_line = self.pool.get('purchase.order.line')
		obj_currency = self.pool.get('res.currency')
		
		data = self.read(cr, uid, ids)[0]
		new_pricelist_id = data['pricelist_id']
		
		porder = obj_po.browse(cr, uid, context['active_id'], context=context)
		
		new_currency = self.pool.get('product.pricelist').browse(cr,uid,new_pricelist_id).currency_id.id
		
		if porder.pricelist_id.currency_id.id == new_currency:
			return {}
		rate = obj_currency.browse(cr, uid, new_currency).rate
		for line in porder.order_line:
			new_price = 0
			if porder.company_id.currency_id.id == porder.pricelist_id.currency_id.id:
				new_price = line.price_unit * rate
				if new_price <= 0:
					raise osv.except_osv(_('Error'), _('New currency is not confirured properly !'))

			if porder.company_id.currency_id.id != porder.pricelist_id.currency_id.id and porder.company_id.currency_id.id == new_currency:
				old_rate = porder.pricelist_id.currency_id.rate
				if old_rate <= 0:
					raise osv.except_osv(_('Error'), _('Currnt currency is not confirured properly !'))
				new_price = line.price_unit / old_rate

			if porder.company_id.currency_id.id != porder.pricelist_id.currency_id.id and porder.company_id.currency_id.id != new_currency:
				old_rate = porder.pricelist_id.currency_id.rate
				if old_rate <= 0:
					raise osv.except_osv(_('Error'), _('Current currency is not confirured properly !'))
				new_price = (line.price_unit / old_rate ) * rate
			obj_po_line.write(cr, uid, [line.id], {'price_unit': new_price})
		obj_po.write(cr, uid, [porder.id], {'pricelist_id': new_pricelist_id})
		return {'type': 'ir.actions.act_window_close'}
purchase_change_pricelist()
