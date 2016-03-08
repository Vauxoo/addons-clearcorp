# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class ResCompany(orm.Model):
    _name = "res.company"
    _inherit = 'res.company'
    _order = 'prefix'

    _columns = {
        'prefix': fields.char('Prefix', size=10),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for obj_company in self.browse(cr, uid, ids, context=context):
            obj_company_name = obj_company.prefix and obj_company.prefix + \
                ' ' or ''
            obj_company_name += obj_company.name
            res.append((obj_company.id, obj_company_name))
        return res
