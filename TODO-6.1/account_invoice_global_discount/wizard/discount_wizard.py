# -*- encoding: utf-8 -*-
##############################################################################
#
#    wizard_discount.py
#    account_invoice_global_discount
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

import pooler
import wizard


_form = """<?xml version="1.0"?>
<form string="Discount:">
    <field name="discount"/>
</form>
"""

_fields = {
    'discount': {
        'string': 'Discount percentage',
        'type': 'float',
        'required': True,
        'default': lambda *args: 0
    },
}


def apply_discount(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    invoice_line_obj = pool.get('account.invoice.line')
    for invoice in invoice_obj.browse(cr, uid, data['ids'], context=context):
        invoice_line_obj.write(cr, uid, [line.id for line in invoice.invoice_line], {'discount': data['form']['discount']}, context=context,)
    return {}


class discount_wizard(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': _form,
                'fields': _fields,
                'state': (('end', 'Cancel'),
                          ('apply_discount', 'Apply Discount', 'gtk-ok', True)
                         )
            }
        },
        'apply_discount': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': apply_discount,
                'state': "end",
            }
        },
    }

discount_wizard('invoice.discount')
