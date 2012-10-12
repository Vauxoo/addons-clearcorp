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
from osv import fields, osv

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    _columns = {
        'name_resource': fields.related('resource_id', 'name', string='Name', type='char', size=128, store=True),
    }
    
    _order = 'name_resource asc'
    
class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    
    _columns = {
        'name_employee': fields.related('employee_id', 'name_resource', string='name_employee', type='char', size=128, store=True),
    }
    
    _order= 'name_employee'

