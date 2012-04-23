# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
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