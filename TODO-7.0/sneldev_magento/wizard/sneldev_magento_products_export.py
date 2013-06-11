# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


import pooler
import os

from export_tools import *
from osv import osv, fields

class wiz_sneldev_products_export(osv.osv_memory):
    _name = 'sneldev.products.export'
    _description = 'Export products'

    _columns = {
        'category_ids': fields.many2many('product.category', 'catg_id', required=True),
        'export_type': fields.selection([('all_products','All products'),('export_by_category','Export by category ')], 'Export type', required=True),
    }

    _defaults = {
    }
    
    def action_add_category(self, cr, uid, ids, context=None):
        wizard_id = ids[0]
        wizard = self.browse(cr, uid, wizard_id, context=context)
        
        category_ids = []
        
        for category in wizard.category_ids:
            category_ids.append(category.id)
     
        return  category_ids  

    def do_products_export(self, cr, uid, ids, context=None):
        wizard_id = ids[0]
        wizard = self.browse(cr, uid, wizard_id, context=context)
        cat_ids = []
        
        if wizard.export_type == 'export_by_category':
            cat_ids = self.action_add_category(cr, uid, ids, context)
            
        result = self.pool.get('sneldev.magento').export_products(cr, uid,cat_ids)   
        
        if result < 0:
            raise osv.except_osv(('Warning'), ('Export failed, please refer to log file for failure details.'))        
        
        return {'type': 'ir.actions.act_window_close'}

wiz_sneldev_products_export()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
