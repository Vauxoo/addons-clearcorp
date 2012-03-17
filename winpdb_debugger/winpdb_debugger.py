# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP
#    Copyright (C) 2009-TODAY (<http://clearcorp.co.cr>).
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
