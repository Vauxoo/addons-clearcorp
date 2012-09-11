#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 SnelDev (http://www.sneldev.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import sys
import traceback
import wizard
import pooler
import os
import xmlrpclib
from xmlrpclib import ServerProxy, Error
from mx import DateTime
import datetime
import threading

#Globals for syncrhonisation
export_lock=threading.Lock();
export_running=False;

#Thread safe version of export_running
def export_is_running():
    global export_running
    
    retVal=False
    export_lock.acquire()  
    if (export_running == False):
        export_running=True
        retVal=False
    else:
        retVal=True  
    export_lock.release()
    return retVal

def set_export_finished():
    global export_running
    export_running=False

def magento_connect(self, cr, uid):
    try:
        ids = self.pool.get('sneldev.magento').search(cr, uid, [])
        export = self.pool.get('sneldev.magento').browse(cr, uid, [ids[0]])
        server_address = export[0]['url']
        if not server_address[-1:] == '/':
            server_address = server_address + "/"
        server_address = server_address + "index.php/api/xmlrpc/?wsdl"
        server = ServerProxy(server_address)
        session = server.login(export[0]['api_user'], export[0]['api_pwd'])
        return [True, server, session]
    except:
        traceback.print_exc()
        return [False, sys.exc_info()[0], False]
            
def to_proper_uni( text):
    return text.encode('iso-8859-1', 'replace')

def to_uni( text ):
    return unicode(text, 'iso-8859-1')

class sneldev_log:
    _logfile = None
    _logs = False

    def __init__(self, filename):
        try:
            self._logfile = open('/var/log/openerp/'+filename , 'a')
        except:
            # Oops
            self._logfile = False
    
    def define(self, logs, cr, uid):
        self._logs = logs
        self._cr = cr
        self._uid = uid
            
    def append(self, log_line):
        try:
          log_line = unicode(log_line).encode('iso-8859-1', 'replace')
        except:
          pass
          
        log_line = str(datetime.datetime.now()).split('.',1)[0] + " " + log_line + "\n"
        if (self._logfile):
            self._logfile.write(log_line)
            self._logfile.flush()
            
        if (self._logs):
            self._logs.create(self._cr, self._uid, {'text': log_line})    
    
    def print_traceback(self):
        traceback.print_exc(file=self._logfile)
        self._logfile.flush()