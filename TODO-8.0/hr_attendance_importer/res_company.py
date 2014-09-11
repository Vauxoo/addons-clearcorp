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

class ResCompany(osv.Model):

    _inherit = 'res.company'

    _columns = {
        'attendance_date_format': fields.char('Date Format', size=32),
        'attendance_sign_in': fields.char('Sign in Action', size=16),
        'attendance_sign_out': fields.char('Sign out Action', size=16),
        'attendance_normal_hours': fields.char('Normal Hours', size=8),
        'attendance_extra_hours': fields.char('Extra Hours', size=8),
        'attendance_default_sign_in': fields.many2one('hr.action.reason', string='Default Sign in reason'),
        'attendance_default_sign_out': fields.many2one('hr.action.reason', string='Default Sign out reason'),
    }