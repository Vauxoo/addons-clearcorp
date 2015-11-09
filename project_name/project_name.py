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
from openerp.osv import osv, fields

class project_name_shortcut(osv.osv):
    _inherit = 'project.project'
    
    def name_get(self, cr, uid, ids=[], context=None):
        res = []
        if isinstance(ids, int):
            ids = [ids]
        done_ids=[]
        for project in self.browse(cr, uid, ids, context=context):
            if project.id not in done_ids:
                data = []
                proj = project.parent_id
                while proj and proj.parent_id:
                    if proj.code != '' and proj.code != False:
                        data.insert(0, (proj.code))
                        proj = proj.parent_id
                        continue
                    else:
                        data.insert(0, (proj.name))
                        proj = proj.parent_id
                data.append(project.name)
                data = ' / '.join(data)
                res.append((project.id, data))
                done_ids.append(project.id)
        return res

    
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=50):
        ids = []
        
        if name:
            ids = self.search(cr, uid,
                              ['|', ('complete_name', operator, name),
                               '|', ('name', operator, name),
                               ('code', operator, name)] + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        analytic_account_ids= [project.analytic_account_id.id for project in self.browse(cr,uid,ids,context=context)] 
        analytic_account_ids= self.pool.get('account.analytic.account').get_children(cr,uid,analytic_account_ids,context=context)
        ids+=self.search(cr,uid,[('analytic_account_id','in',analytic_account_ids)],context=context)
        
        return self.name_get(cr, uid, ids, context=context)
    
class account_name_shortcut(osv.osv):
    _inherit = 'account.analytic.account'
    
    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=50):
        ids = []
        
        if name:
            ids = self.search(cr, uid,
                              ['|', ('complete_name', operator, name),
                               '|', ('name', operator, name),
                               ('code', operator, name)] + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        ids+= self.get_children(cr,uid,ids,context=context)
        
        return self.name_get(cr, uid, ids, context=context)