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

class wiz_sneldev_orders_import(osv.osv_memory):
    _name = 'sneldev.orders.import'
    _description = 'Import orders'

    _columns = {
    }

    _defaults = {
    }

    def do_orders_import(self, cr, uid, ids, context=None):
        self.pool.get('sneldev.magento').import_categories(cr, uid)
        self.pool.get('sneldev.magento').import_products(cr, uid)
        entity_id = '';
        increment_id = '';
        
        if (self.pool.get('sneldev.magento').import_orders(cr, uid,entity_id,increment_id) < 0):
            raise osv.except_osv(('Warning'), ('Import failed, please refer to log file for failure details.'))
        
        if (self.pool.get('sneldev.magento').import_credit_memos(cr, uid) < 0):
            raise osv.except_osv(('Warning'), ('Import failed, please refer to log file for failure details.'))
       
        return {'type': 'ir.actions.act_window_close'}

wiz_sneldev_orders_import()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
