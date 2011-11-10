# -*- encoding: utf-8 -*-
##############################################################################
#
#    invoice.py
#    ccorp_sale
#    First author: Mag Guevara <mag.guevara@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2010-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
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

import time
import pooler
from report import report_sxw
import locale

class purchase_order_ccorp(report_sxw.rml_parse):

	def _get_line_tax(self, line_obj):
		self.cr.execute("SELECT tax_id FROM purchase_order_taxe WHERE order_line_id=%s", (line_obj.id))
		res = self.cr.fetchall() or None
		if not res:
			return ""
		if isinstance(res, list):
			tax_ids = [t[0] for t in res]
		else:
			tax_ids = res[0]
		res = [tax.name for tax in pooler.get_pool(self.cr.dbname).get('account.tax').browse(self.cr, self.uid, tax_ids)]
		return ",\n ".join(res)
	
	def _get_tax(self, order_obj):
		self.cr.execute("SELECT DISTINCT tax_id FROM purchase_order_taxe, purchase_order_line, purchase_order \
			WHERE (purchase_order_line.order_id=purchase_order.id) AND (purchase_order.id=%s)", (order_obj.id))
		res = self.cr.fetchall() or None
		if not res:
			return []
		if isinstance(res, list):
			tax_ids = [t[0] for t in res]
		else:
			tax_ids = res[0]
		tax_obj = pooler.get_pool(self.cr.dbname).get('account.tax')
		res = []
		for tax in tax_obj.browse(self.cr, self.uid, tax_ids):
			self.cr.execute("SELECT DISTINCT order_line_id FROM purchase_order_line, purchase_order_taxe \
				WHERE (purchase_order_taxe.tax_id=%s) AND (purchase_order_line.order_id=%s)", (tax.id, order_obj.id))
			lines = self.cr.fetchall() or None
			if lines:
				if isinstance(lines, list):
					line_ids = [l[0] for l in lines]
				else:
					line_ids = lines[0]
				base = 0
				for line in pooler.get_pool(self.cr.dbname).get('purchase.order.line').browse(self.cr, self.uid, line_ids):
					base += line.price_subtotal
				res.append({'code':tax.name,
					'base':base,
					'amount':base*tax.amount})
		return res
	def _get_product_code(self, product_id, partner_id):
		product_obj=pooler.get_pool(self.cr.dbname).get('product.product')
		return product_obj._product_code(self.cr, self.uid, [product_id], name=None, arg=None, context={'partner_id': partner_id})[product_id]

	def __init__(self, cr, uid, name, context):
		super(purchase_order_ccorp, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'time': time,
			'get_line_tax': self._get_line_tax,
			'get_tax': self._get_tax,
			'get_product_code': self._get_product_code,
			'cr'  : cr,
			'uid' : uid,
		})
		self.context = context
		self._node = None

report_sxw.report_sxw(
    'report.purchase.order.layout_ccorp',
    'purchase.order',
    'addons/ccorp_purchase/report/purchase_order.mako',
    parser=purchase_order_ccorp
)
