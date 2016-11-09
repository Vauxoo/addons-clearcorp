
# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Addons modules by CLEARCORP S.A.
# Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,related relationrelated relation
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields, orm

class ResPartner(orm.Model):
    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for partner in self.browse(cr, uid, ids, context=context):
            partner_name = ''
            if partner.trade_name:
                partner_name += partner.name + \
                    ' ' + '['+partner.trade_name+']'
            else:
                partner_name += partner.name
            res.append((obj_company.id, obj_company_name))
        return res

    def name_search(self, cr, uid, name, args = None, operator = 'ilike',
                    context=None, limit = 100):
        res = super(ResPartner, self).name_search(cr, uid, name,
                        args = args, operator = 'ilike', context = context)
        ids = self.search(cr, uid, [('trade_name', operator, name)],
                              limit = limit, context = context)
        res = list(set(res + self.name_get(cr, uid, ids, context)))
        return res

    _columns={
            'trade_name': fields.char('Trade Name', size=128, 
                                        help="Is used if " + \
                                            "the contact used trade " + \
                                            "name, and this is different " + \
                                            "to the business name"),
            }
