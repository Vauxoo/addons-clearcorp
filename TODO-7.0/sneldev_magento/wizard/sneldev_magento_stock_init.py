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

class wiz_sneldev_stock_init(osv.osv_memory):
    _name = 'sneldev.stock.init'
    _description = 'Initialize stock from Magento'

    _columns = {
    }

    _defaults = {
    }

    def do_stock_init(self, cr, uid, ids, context=None):
        if (self.pool.get('sneldev.magento').init_stock(cr, uid) < 0):
            raise osv.except_osv(('Warning'), ('Init failed, please refer to log file for failure details.'))
        
        return {'type': 'ir.actions.act_window_close'}

wiz_sneldev_stock_init()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
