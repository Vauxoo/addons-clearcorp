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

from osv import fields, orm
from tools.translate import _

class accountConfigsettingsInherit(orm.Model):
    
    _inherit = 'account.config.settings'
    
    _columns = {
        'max_discount': fields.related('company_id', 'max_discount',type='float', string="Max Discount",), 
    }
    
    """Override onchange_company_id to update max_discount """ 
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(accountConfigsettingsInherit, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'max_discount':company.max_discount})
        return res
    
    """Get the default max_discount"""
    def get_default_max_discount(self, cr, uid, fields, context=None):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'account.invoice.limit.discount', context=context) #module name
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'max_discount': company.max_discount}
    
    """Set the default max_discount in the selected company"""
    def set_attendance_date_format(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        config.company_id.write({'max_discount': config.max_discount})
    