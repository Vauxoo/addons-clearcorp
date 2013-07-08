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

class wiz_sneldev_categories_export(osv.osv_memory):
    _name = 'sneldev.categories.export'
    _description = 'Export categories'

    _columns = {
    }

    _defaults = {
    }

    def do_categories_export(self, cr, uid, ids, context=None):
        #self.pool.get('sneldev.magento').export_categories(cr, uid)
        if (self.pool.get('sneldev.magento').export_categories(cr, uid) < 0):
            raise osv.except_osv(('Warning'), ('Export failed, please refer to log file for failure details.'))
        
        return {'type': 'ir.actions.act_window_close'}

wiz_sneldev_categories_export()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
