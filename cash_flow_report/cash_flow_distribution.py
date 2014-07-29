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

from osv import fields, orm

class cashFlowdistribution(orm.Model):
    _name = "cash.flow.distribution"
    _inherit = "account.distribution.line"
    _description = "Cash Flow Distribution"

    _defaults = {
        'type': 'manual', 
        'distribution_amount': 0.0,
        'distribution_percentage': 0.0,
    }
    
    def create(self, cr, uid, vals, context=None):
        if context:
            dist_type = context.get('distribution_type','auto')
        else:
            dist_type = 'auto'
        vals['type'] = dist_type
        res = super(cashFlowdistribution, self).create(cr, uid, vals, context)
        return res