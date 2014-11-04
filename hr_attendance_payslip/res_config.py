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

class Config(osv.TransientModel):

    _inherit = 'hr.config.settings'

    def onchange_attendance_company(self, cr, uid, ids, attendance_company_id, context=None):
        res = super(Config, self).onchange_attendance_company(cr, uid, ids,
            attendance_company_id, context=context)
        vals = {}
        if 'value' in res.keys():
            if attendance_company_id:
                company_obj = self.pool.get('res.company')
                company= company_obj.browse(cr, uid, attendance_company_id, context=context)
                vals = {
                    'attendance_payslip_use_default': company.attendance_payslip_use_default,
                    'attendance_payslip_normal_hours': company.attendance_payslip_normal_hours,
                    'attendance_payslip_extra_hours': company.attendance_payslip_extra_hours,
                }
            else:
                vals = {
                    'attendance_payslip_use_default': 0.0,
                    'attendance_payslip_normal_hours': 0.0,
                    'attendance_payslip_extra_hours': 0.0,
                }
        else:
            vals = {
                'attendance_payslip_use_default': 0.0,
                'attendance_payslip_normal_hours': 0.0,
                'attendance_payslip_extra_hours': 0.0,
            }
        res['value'].update(vals)
        return res

    def get_default_attendance_payslip_use_default(self, cr, uid, fields, context=None):
        """Get the default attendance_payslip_use_default"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.payslip', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_payslip_use_default': company.attendance_payslip_use_default}

    def set_attendance_payslip_use_default(self, cr, uid, ids, context=None):
        """Set the new attendance_payslip_use_default in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_payslip_use_default': config.attendance_payslip_use_default})

    def get_default_attendance_payslip_normal_hours(self, cr, uid, fields, context=None):
        """Get the default attendance_payslip_normal_hours"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.payslip', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_payslip_normal_hours': company.attendance_payslip_normal_hours}

    def set_attendance_payslip_normal_hours(self, cr, uid, ids, context=None):
        """Set the new attendance_payslip_normal_hours in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_payslip_normal_hours': config.attendance_payslip_normal_hours})

    def get_default_attendance_payslip_extra_hours(self, cr, uid, fields, context=None):
        """Get the default attendance_payslip_extra_hours"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.payslip', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_payslip_extra_hours': company.attendance_payslip_extra_hours}

    def set_attendance_payslip_extra_hours(self, cr, uid, ids, context=None):
        """Set the new attendance_payslip_extra_hours in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_payslip_extra_hours': config.attendance_payslip_extra_hours})

    _columns = {
        'attendance_payslip_use_default': fields.boolean('Use Default Values',
            help='Used the default values below when there are no hours from'
            ' services. If value is 0 will be ignored'),
        'attendance_payslip_normal_hours': fields.float('Normal Hours', digits=(16,2)),
        'attendance_payslip_extra_hours': fields.float('Extra Hours', digits=(16,2)),
    }