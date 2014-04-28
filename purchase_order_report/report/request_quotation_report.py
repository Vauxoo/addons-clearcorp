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

import time
import pooler
from report import report_sxw
import locale

class purchase_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(purchase_order_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process_purcharse_lines':self.process_purcharse_lines,
        })
    
    def process_purcharse_lines(self, purchase_order):
        lines = {}
        name = ''
        find_name = False
         
        for line in purchase_order.order_line:
            if line.product_id: 
                if line.product_id.seller_ids:
                    for seller in line.product_id.seller_ids:
                        if seller.name.id == purchase_order.partner_id.id:
                            if seller.product_code and seller.product_name:
                                name = "["+seller.product_code+"] "+ seller.product_name                            
                            elif seller.product_code and not seller.product_name:
                                name = "["+seller.product_code+"] "+ line.product_id.name
                            elif not seller.product_code and seller.product_name:
                                name = "["+line.product_id.default_code+"] "+ seller.product_name
                            find_name = True
                            break     
                    if not find_name:
                       lines[line.id] = line.name 
                else:
                    lines[line.id] = line.name                             
            else:
                lines[line.id] = line.name
        
        return lines
    
#the parameters are the report name and module name 
report_sxw.report_sxw('report.purchase_quotation_report_inherit',
                      'purchase.order',
                      'addons/purchase_order_report/report/purchase_order_report.mako',
                      parser=purchase_order_report)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
