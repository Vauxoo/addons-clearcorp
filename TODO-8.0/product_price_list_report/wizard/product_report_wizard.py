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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_price_list(osv.osv_memory):
    _inherit = 'product.price_list'
    
    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        
        datas = {'ids': context.get('active_ids', [])}
        #Read values
        res = self.read(cr, uid, ids, ['price_list','qty1', 'qty2','qty3','qty4','qty5'], context=context)
        res = res and res[0] or {}
        #Extract id for m2o fields
        res['price_list'] = res['price_list'][0]
        #Update dictionary
        datas['form'] = res
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'product_price_list_report_odt',
            'datas': datas,
       }