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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class accountPeriodinherit(orm.Model):
    _name = 'account.period'
    _inherit = 'account.period'
    
    def _get_reports_account_period(self, cr, uid, ids, field_name, arg, context=None):
        period = self.browse(cr, uid, ids[0], context)
        result = {}

        result[period.id] = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.period'),('res_id','=',period.id)])
        
        return result    
    
    _columns = {
        'file_ids': fields.function(_get_reports_account_period, type='one2many', obj = 'ir.attachment', string='Attachments', readonly=True),
    }
