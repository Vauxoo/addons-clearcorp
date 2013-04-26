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

class DiscountWizard(osv.osv):

    _name = "discount.wizard"
    _description = "Discount Wizard"
    
    _columns = {
        'discount': fields.float('Discount percentage', required=True),
        'period_from': fields.many2one('account.period', 'Start Period'),
        'period_to': fields.many2one('account.period', 'End Period'),
    }
    
    _default = {
        'discount': lambda *args: 0
    }
                
        
    def apply_discount(self, cr, uid, data, context):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        for invoice in invoice_obj.browse(cr, uid, data['ids'], context=context):
            invoice_line_obj.write(cr, uid, [line.id for line in invoice.invoice_line], {'discount': data['form']['discount']}, context=context,)
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

