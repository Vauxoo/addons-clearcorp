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

class Employee(osv.Model):

    _inherit = 'hr.employee'

    _columns = {
                'code': fields.char('Code', size=64),
                }

    _sql_constraints = [('unique_code','UNIQUE(code)','The code must be unique for every employee.')]

"""class ActionReason(osv.Model):

    _inherit = 'hr.action.reason'

    def __init__(self, pool, cr):
        super(ActionReason,self)._columns['action_type'].selection.append(('action','Action'))

    _sql_constraints = [('unique_code','UNIQUE(code)','The code must be unique for every employee.')]"""