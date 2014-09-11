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

class ResConfig(osv.TransientModel):

    _inherit = 'hr.config.settings'

    def get_default_pay_commission_company_id(self, cr, uid, fields, context=None):
        """Get the default company for the module"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.config.settings', context=context)
        return {'pay_commission_company_id': company_id}

    def get_default_pay_commission_name(self, cr, uid, fields, context=None):
        """Get the default company commission name"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.config.settings', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'pay_commission_name': company.pay_commission_name}

    def set_pay_commission_name(self, cr, uid, ids, context=None):
        """Set the new pay_commission_name in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.pay_commission_company_id.write({'pay_commission_name': config.pay_commission_name})

    def get_default_pay_commission_code(self, cr, uid, fields, context=None):
        """Get the default company commission code"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.config.settings', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'pay_commission_code': company.pay_commission_code}

    def set_pay_commission_code(self, cr, uid, ids, context=None):
        """Set the new pay_commission_code in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.pay_commission_company_id.write({'pay_commission_code': config.pay_commission_code})

    def get_default_pay_commission_sequence(self, cr, uid, fields, context=None):
        """Get the default company commission sequence"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.config.settings', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'pay_commission_sequence': company.pay_commission_sequence}

    def set_pay_commission_sequence(self, cr, uid, ids, context=None):
        """Set the new pay_commission_sequence in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.pay_commission_company_id.write({'pay_commission_sequence': config.pay_commission_sequence})

    _columns = {
        'pay_commission_company_id': fields.many2one('res.company', string='Company', required=True),
        'pay_commission_name': fields.char('Name', size=128),
        'pay_commission_code': fields.char('Code', size=16),
        'pay_commission_sequence': fields.integer('Sequence'),
    }