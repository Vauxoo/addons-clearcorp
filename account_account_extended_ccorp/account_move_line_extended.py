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

from osv import osv,fields, orm

class accountMovelineInherit(orm.Model):
    
    _inherit = "account.move.line"
    
    #===== Add currency and account_type with two function fields
     
    #===== Currency -> get currency_id from company_id or account_id
    def _currency_filter(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.account_id.currency_id:
                result[rec.id] = (rec.account_id.currency_id.id,rec.account_id.currency_id.name)
            else:
                result[rec.id] = (rec.company_id.currency_id.id,rec.company_id.currency_id.name)
        return result
    
    #====== Account Type -> get user_type from account_id
    def _account_type_filter(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
             result[rec.id] = (rec.account_id.user_type.id, rec.account_id.user_type.name)
        return result

    _columns = {        
        'currency_filter':fields.function(_currency_filter, string='Currency', type="many2one", relation='res.currency',store=True),
        'account_type':fields.function(_account_type_filter, string='Account Type', type='many2one', relation='account.account.type',store=True)
        }
    
    
    
    