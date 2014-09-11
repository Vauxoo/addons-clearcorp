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

class ResCompany(osv.Model):

    _inherit = 'res.company'

    _columns = {
        'pay_commission_name': fields.char('Commission Name', size=32),
        'pay_commission_code': fields.char('Commission Code', size=16),
        'pay_commission_sequence': fields.integer('Commission Sequence'),
    }

    _defaults = {
        'pay_commission_name': _('Commission'),
        'pay_commission_code': 'COM',
        'pay_commission_sequence': 0,
    }