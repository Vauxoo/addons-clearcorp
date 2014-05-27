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

    def onchange_attendance_company(self, cr, uid, ids, attendance_company_id, context=None):
        vals = {}
        if attendance_company_id:
            company_obj = self.pool.get('res.company')
            company= company_obj.browse(cr, uid, attendance_company_id, context=context)
            vals = {
                'attendance_date_format': company.attendance_date_format,
                'attendance_sign_in': company.attendance_sign_in,
                'attendance_sign_out': company.attendance_sign_out,
                'attendance_normal_hours': company.attendance_normal_hours,
                'attendance_extra_hours': company.attendance_extra_hours,
                'attendance_default_sign_in': company.attendance_default_sign_in.id,
                'attendance_default_sign_out': company.attendance_default_sign_out.id,
            }
        else:
            vals = {
                'attendance_date_format': False,
                'attendance_sign_in': False,
                'attendance_sign_out': False,
                'attendance_normal_hours': False,
                'attendance_extra_hours': False,
                'attendance_default_sign_in': False,
                'attendance_default_sign_out': False,
            }
        return {'value': vals}

    def get_default_attendance_company_id(self, cr, uid, fields, context=None):
        """Get the default company for the module"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        return {'attendance_company_id': company_id}

    def get_default_attendance_date_format(self, cr, uid, fields, context=None):
        """Get the default company date_format"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_date_format': company.attendance_date_format}

    def set_attendance_date_format(self, cr, uid, ids, context=None):
        """Set the new attendance_date_format in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_date_format': config.attendance_date_format})

    def get_default_attendance_sign_in(self, cr, uid, fields, context=None):
        """Get the default company sign in action"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_sign_in': company.attendance_sign_in}

    def set_attendance_sign_in(self, cr, uid, ids, context=None):
        """Set the new attendance_sign_in in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_sign_in': config.attendance_sign_in})

    def get_default_attendance_sign_out(self, cr, uid, fields, context=None):
        """Get the default company sign out action"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_sign_out': company.attendance_sign_out}

    def set_attendance_sign_out(self, cr, uid, ids, context=None):
        """Set the new attendance_sign_out in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_sign_out': config.attendance_sign_out})

    def get_default_attendance_normal_hours(self, cr, uid, fields, context=None):
        """Get the default company normal hours identifier"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_normal_hours': company.attendance_normal_hours}

    def set_attendance_normal_hours(self, cr, uid, ids, context=None):
        """Set the new attendance_normal_hours in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_normal_hours': config.attendance_normal_hours})

    def get_default_attendance_extra_hours(self, cr, uid, fields, context=None):
        """Get the default company extra hours identifier"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_extra_hours': company.attendance_extra_hours}

    def set_attendance_extra_hours(self, cr, uid, ids, context=None):
        """Set the new attendance_extra_hours in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_extra_hours': config.attendance_extra_hours})

    def get_default_attendance_default_sign_in(self, cr, uid, fields, context=None):
        """Get the default attendance_sign_in"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_default_sign_in': company.attendance_default_sign_in.id}

    def set_attendance_default_sign_in(self, cr, uid, ids, context=None):
        """Set the new attendance_default_sign_in in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_default_sign_in': config.attendance_default_sign_in.id})

    def get_default_attendance_default_sign_out(self, cr, uid, fields, context=None):
        """Get the default attendance_sign_out"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_default_sign_out': company.attendance_default_sign_out.id}

    def set_attendance_default_sign_out(self, cr, uid, ids, context=None):
        """Set the new attendance_default_sign_out in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_default_sign_out': config.attendance_default_sign_out.id})

    _columns = {
        'attendance_company_id': fields.many2one('res.company', string='Company', required=True),
        'attendance_date_format': fields.char('Date format when importing files', size=32,
            help='Python date format used when importing files'),
        'attendance_sign_in': fields.char('Identifier for sign in actions', size=16),
        'attendance_sign_out': fields.char('Identifier for sign out actions', size=16),
        'attendance_normal_hours': fields.char('Identifier for normal hours', size=8),
        'attendance_extra_hours': fields.char('Identifier for extra hours', size=8),
        'attendance_default_sign_in': fields.many2one('hr.action.reason', string='Default Sign in reason'),
        'attendance_default_sign_out': fields.many2one('hr.action.reason', string='Default Sign out reason'),
    }