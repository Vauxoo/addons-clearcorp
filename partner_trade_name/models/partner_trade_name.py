# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            res.append((partner.id, partner_name))
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
