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

from osv import fields,osv

class res_company(osv.osv):
    _name = 'res.company'
    _inherit = 'res.company'
    
    _columns = {
            'payslip_footer':fields.text('Payslip footer'),
    }
res_company()

class HrSalaryRule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'appears_on_report': fields.boolean('Appears on Report', help="Used for the display of rule on payslip reports"),
    }
    
    _defaults = {
        'appears_on_report': True,
    }

