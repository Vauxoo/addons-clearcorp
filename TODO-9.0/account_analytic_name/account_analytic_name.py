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

class account_name_shortcut(osv.osv):
    _inherit = 'account.analytic.account'
    
    def name_get(self, cr, uid, ids=[], context=None):
        res = []
        if isinstance(ids, int):
            ids = [ids]
        done_ids=[]
        for account in self.browse(cr, uid, ids, context=context):
            if account.id not in done_ids:
                data = []
                parent_account = account.parent_id
                while parent_account and parent_account.parent_id:
                    if parent_account.code != '' and parent_account.code != False:
                        data.insert(0, (parent_account.code))
                        parent_account = parent_account.parent_id
                        continue
                    else:
                        data.insert(0, (parent_account.name))
                        parent_account = parent_account.parent_id
                data.append(account.name)
                data = ' / '.join(data)
                res.append((account.id, data))
                done_ids.append(account.id)
        return res
    
    def get_children(self,cr,uid,ids,context=None):
        res=[]
        for account in self.browse(cr,uid,ids,context=context):
            if account.child_ids:
                child_ids=[]
                for child in account.child_ids:
                    child_ids.append(child.id)
                res+= child_ids
                res+=self.get_children(cr,uid,child_ids,context=context)
                    
                
        return res
        

    def complete_name_compute(self, cr, uid, ids, field_name, arg, context=None):
        return self.name_get(cr, uid, ids, context=context)
        
    _columns = {
        'complete_name':  fields.function(complete_name_compute, store={
                                                 'account.analytic.account':(lambda self, cr, uid, ids, context=None: ids+self.get_children(cr,uid,ids,context=context), ['code','name'],5)                              
                                                 }, 
                                          string='Full Name', type='char', size=350, method=True),
    }
    
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