# -*- encoding: utf-8 -*-
##############################################################################
#
#
#    payment_receipt
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
from amount_to_text import number_to_text_es
import locale

class payment_receipt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(payment_receipt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr' : cr,
            'uid': uid,
            'get_text':self.get_text,
        })
            
    def get_text(self,amount,currency,lang,company_id):
        separator = ','
        decimal_point = '.'
        name_currency = currency.currency_name
        if name_currency == False:
            name_currency = company_id.currency_id.currency_name
        if name_currency == None:
            name_currency = company_id.currency_id.currency_name
        if lang:
            lang_pool = self.pool.get('res.lang')
            id_lang = lang_pool.search(self.cr,self.uid,[('code','=',lang)])
            obj_lang = lang_pool.browse(self.cr,self.uid,id_lang)[0]
            separator = obj_lang  and obj_lang.thousands_sep or separator
            decimal_point = obj_lang  and obj_lang.decimal_point or decimal_point
        res = number_to_text_es(amount,name_currency,separator=separator,decimal_point=decimal_point)
        return res
        
report_sxw.report_sxw(
    'report.account.voucher.layout_ccorp',
    'account.voucher',
    'addons/ccorp_payment_receipt/report/payment_receipt.mako',
    parser=payment_receipt)
