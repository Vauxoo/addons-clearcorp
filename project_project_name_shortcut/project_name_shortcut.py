# -*- encoding: utf-8 -*-
##############################################################################
#
#    __openerp__.py
#    project_hierarchical_name
#    First author: David Murillo <david.murillo@clearcorp.co.cr> (ClearCorp S.A.)
#    Second author: Mag Guevara <mag.guevara@clearcorp.co.cr> (ClearCorp S.A.)
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
#from tools import #debug


class project_name_shortcut(osv.osv):
    _name = 'project.project'
    _inherit = 'project.project'
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for project in self.browse(cr, uid, ids, context=context):
            data = []
            proj = project.parent_id
            while proj :
                if proj.code != '' and proj.code != False:
                    data.insert(0,(proj.name))
                    proj = proj.parent_id
                    continue
                else:
                    data.insert(0,(proj.name))
                    proj = proj.parent_id
                
                
            
            data.append(project.name)
            data = ' / '.join(data)
            res.append((project.id, data))
        return res

    def _shortcut_name(self, cr, uid, ids,field_name,arg, context=None):
        res ={}
        #debug(ids)
        for m in self.browse(cr,uid,ids,context=context):
            res = self.name_get(cr, uid, ids)
            return dict(res)

        return res
        
    _columns = {
        'shortcut_name': fields.function(_shortcut_name, method=True, string='Project Name', type='char', size=350),
        'shortcut': fields.char('shortcut',size=16),
    }
project_name_shortcut()


