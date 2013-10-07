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

class hr_expense_line(osv.osv):
    _name = "hr.expense.line"
    _inherit = 'hr.expense.line'
    
    _columns = {
                'res_partner_id': fields.many2one('res.partner', 'Supplier', domain=[('supplier','=',True)] ),
                }   
    
    
    ##commercial_partner_id

class hr_expense_expense(osv.osv):
    _name = "hr.expense.expense"
    _inherit = 'hr.expense.expense'
    
    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(hr_expense_expense, self).move_line_get_item(cr, uid, line, context=context)
        if line.res_partner_id and line.res_partner_id.commercial_partner_id\
            and line.res_partner_id.commercial_partner_id.id:
            #res['exp_line_partner_id']= line.res_partner_id.commercial_partner_id.id
            res['exp_line_partner_id']= line.res_partner_id.id
        return res
    
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        new_part = partner_obj = self.pool.get('res.partner')
        if 'exp_line_partner_id' in x.keys():
            new_part_list = partner_obj.browse(cr, uid, [x['exp_line_partner_id']], context=context)
            new_part = new_part_list[0] if new_part_list else part
            x.pop('exp_line_partner_id', None)
        else:
            new_part = part
        res = super(hr_expense_expense, self).line_get_convert(cr, uid, x, new_part, date, context=context)
        return res

    
