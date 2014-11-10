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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class Config(osv.TransientModel):

    _inherit = 'sale.config.settings'

    def onchange_limit_discount_company_id(self, cr, uid, ids,
        limit_discount_company_id, context=None):
        vals = {}
        if limit_discount_company_id:
            company_obj = self.pool.get('res.company')
            company= company_obj.browse(cr, uid,
                limit_discount_company_id, context=context)
            vals = {
                'limit_discount_active': company.limit_discount_active,
                'limit_discount_max_discount': company.limit_discount_max_discount,
            }
        else:
            vals = {
                'limit_discount_active': False,
                'limit_discount_max_discount': False,
            }
        return {'value': vals}

    def get_default_limit_discount_company_id(self, cr, uid, fields, context=None):
        """Get the default company for the module"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid,
            'sale.max.discount', context=context)
        return {'limit_discount_company_id': company_id}

    def get_default_limit_discount_active(self, cr, uid, fields, context=None):
        """Get the default company limit_discount_active"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid,
            'sale.max.discount', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'limit_discount_active': company.limit_discount_active}

    def set_limit_discount_active(self, cr, uid, ids, context=None):
        """Set the new limit_discount_active in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.limit_discount_company_id.write(
            {'limit_discount_active': config.limit_discount_active})

    def get_default_limit_discount_max_discount(self, cr, uid, fields, context=None):
        """Get the default company limit_discount_max_discount"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid,
            'sale.max.discount', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'limit_discount_max_discount': company.limit_discount_max_discount}

    def set_limit_discount_max_discount(self, cr, uid, ids, context=None):
        """Set the new limit_discount_max_discount in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.limit_discount_company_id.write(
            {'limit_discount_max_discount': config.limit_discount_max_discount})

    _columns = {
        'limit_discount_company_id': fields.many2one('res.company', string='Company',
            required=True),
        'limit_discount_active': fields.boolean('Discount Applicable'),
        'limit_discount_max_discount': fields.float('Max Discount',
            digits_compute=dp.get_precision('Discount'),
            help='Max discount allowed in sales.'),
    }