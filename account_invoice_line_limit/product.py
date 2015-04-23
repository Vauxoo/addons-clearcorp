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
from openerp.osv import osv,fields
from openerp.tools.translate import _
import re

class product_template(osv.osv):
    _inherit = "product.template"
    def create(self, cr, uid, vals, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if 'description' in vals:
            if len(vals.get('description'))>user.company_id.maximum_description_product:
                raise osv.except_osv(_('Error!'), _('The product description exceeds the limit of %i characters.' %user.company_id.maximum_description_product))
        result = super(product_template, self).create(cr, uid, vals, context=context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if 'description' in vals:
            if len(vals.get('description'))>user.company_id.maximum_description_product:
                raise osv.except_osv(_('Error!'), _('The product description exceeds the limit of %i characters.' %user.company_id.maximum_description_product))
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        return res
class product_product(osv.osv):
    _inherit = "product.product"
    def create(self, cr, uid, vals, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if 'description' in vals:
            if len(vals.get('description'))>user.company_id.maximum_description_product:
                raise osv.except_osv(_('Error!'), _('The product description exceeds the limit of %i characters.' %user.company_id.maximum_description_product))
        result = super(product_product, self).create(cr, uid, vals, context=context)
        return result
    
    def write(self, cr, uid, ids, vals, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if 'description' in vals:
            if len(vals.get('description'))>user.company_id.maximum_description_product:
                raise osv.except_osv(_('Error!'), _('The product description exceeds the limit of %i characters.' %user.company_id.maximum_description_product))
        res = super(product_product, self).write(cr, uid, ids, vals, context=context)
        return res