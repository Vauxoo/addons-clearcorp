# -*- encoding: utf-8 -*-
##############################################################################
#
#    __terp__.py
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

{
    'name': 'ClearCorp report module for voucher and other payments',
    'version': '0.1',
    'url': 'http://launchpad.net/openerp-costa-rica',
    'author': 'CLEARCORP S.A.',
    'website': 'http://clearcorp.co.cr',
    'category': '',
    'description': """ClearCorp 'reports' for vouchers:
    Reports:
      * Voucher
    """,
    'depends': [
        'account',
        'account_voucher_payment_method',
        'base_currency_symbol',
        'report_webkit',
        ],
    'init_xml': [],
    'update_xml': [
        'payment_receipt_report.xml', 
        ],
    'license': 'Other OSI approved licence',
    'installable': True,
    'active': False,
}
