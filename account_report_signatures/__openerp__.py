# -*- encoding: utf-8 -*-
##############################################################################
#
#    account_report_signatures
#    First author: Diana Rodríguez <diana.rodriguez@clearcorp.co.cr> (ClearCorp S.A.)
#    Copyright (c) 2013-TODAY ClearCorp S.A. (http://clearcorp.co.cr). All rights reserved.
#    Inspired directly from Camp2Camp module c2c_currency_rate_update
#    The module was copied and modified in order to provide enough flexibility to extend it
#    to use as a generic WebService XML data importer into OpenERP.
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
    'name': 'Account report signatures',
    'version': '0.1',
    'url': 'http://launchpad.net/openerp-ccorp-addons',
    'author': 'ClearCorp S.A',
    'website': 'http://clearcorp.co.cr',
    'category': 'Generic Modules/Base',
    'description': """ Add the users that can signature the reports.""",
    'depends': ['base', 'account','hr'],
    'init_xml': [],
    'demo_xml': [],
    'data': [ 'security/hr_security.xml',
              'account_report_signatures.xml',
              'account_report_signature_menu.xml'],
    'license': 'Other OSI approved licence',
    'installable': True,
    'active': False,
}
