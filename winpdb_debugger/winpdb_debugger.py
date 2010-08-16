# -*- encoding: utf-8 -*-
##############################################################################
#
#    winpdb_debugger.py
#    winpdb_debugger
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

import wizard
import osv
from tools import config

import rpdb2

ask_form ='''<?xml version="1.0"?>
<form string="Winpdb debugger">
    <label string="Open Winpdb and set the password to the OpenERP server administrator password. Then clic 'Start Winpdb debugger'." colspan="4"/>
    <label string="The system will wait for 5 minutes until you open a connection. If no connection is opened, the server will continue." colspan="4"/>
</form>
'''

finish_form ='''<?xml version="1.0"?>
<form string="Winpdb debugger">
    <label string="Winpdb attached or timeout." colspan="4"/>
</form>
'''

class winpdb_debugger_wizard(wizard.interface):
    def start_debugger(self, cr, uid, data, context):
        rpdb2.start_embedded_debugger(config['admin_passwd'])
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': ask_form,
                'fields': {},
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('start', 'Start Winpdb debugger', 'gtk-ok', True)
                ]
            }
        },
        'start': {
            'actions': [start_debugger],
            'result': {
                'type':'form',
                'arch':finish_form,
                'fields':{},
                'state':[('end','Close')]
            }
        },
    }
winpdb_debugger_wizard('winpdb.debugger')
