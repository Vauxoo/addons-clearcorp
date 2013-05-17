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
from osv import fields, osv

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    _columns= {
    'budget_program_line': fields.many2one('budget.program.line', 'Budget line'),
    'budget_move': fields.many2one('budget.move', 'Budget move' )
    }
    
    def create(self, cr, uid, vals, context=None):
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        obj_order = self.browse(cr,uid,[order],context=context)[0]
        
        bud_move_obj = self.pool.get('budget.move')
        move_id = bud_move_obj.create(cr, uid, {'origin':obj_order.name, 'program_line_id': vals['budget_program_line'],'reserved': obj_order.amount_total }, context=context)
        self.write(cr, uid,[order],{'budget_move':move_id})
        
        return order