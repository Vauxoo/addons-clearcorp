# -*- encoding: utf-8 -*-
##############################################################################
#
#    First author: Diana Rodríguez <diana.rodriguez@clearcorp.co.cr> (ClearCorp S.A.)
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
from tools.translate import _

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not len(ids):
            return []
        if context.get('show_ref'):
            rec_name = 'ref'
        else:
            rec_name = 'name'
            
        """The method read receive a items list that it needs to read and show
            for example, if we need to show the ref and name item, the list is of this wave:
            [name, ref].
            self.read(cr,uid,ids,[name,ref],context) 
        """
        res = [(r['id'],r[rec_name]) for r in self.read(cr, uid, ids, [rec_name,'ref'], context)]

        return res
  
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []

        if name and operator in ('=', 'ilike', '=ilike', 'like'):
            """We need all the partners that match with the ref or name (or a part of them)"""
            ids = self.search(cr, uid, ['|',('ref', 'ilike', name),('name','ilike',name)] + args, limit=limit, context=context)
            if ids and len(ids) > 0:
                return self.name_get(cr, uid, ids, context)
        return super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
    
    
    