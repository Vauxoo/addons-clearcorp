# -*- encoding: utf-8 -*-
##############################################################################
#
#    invoice.py
#    ccorp_sale
#    First author: Carlos Vásquez <carlos.vasquez@clearcorp.co.cr> (ClearCorp S.A.)
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

class sale_order_ccorp(report_sxw.rml_parse):

    def sale_order_ccorp_discount(self, sale_order):
        res = 0
        line_ids = self.pool.get('sale.order.line').search(self.cr, self.uid, [('order_id', '=', sale_order.id)])
        for line in line_ids:
            line_info = self.pool.get('sale.order.line').browse(self.cr, self.uid, id, self.context.copy())
            res += line.price_subtotal * line.discount / 100
        return res

    def __init__(self, cr, uid, name, context):
        super(sale_order_ccorp, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'discount': self.sale_order_ccorp_discount,
        })

report_sxw.report_sxw(
    'report.sale.order.layout_ccorp',
    'sale.order',
    'addons/ccorp_sale/report/sale_order.rml',
    parser=sale_order_ccorp
)
