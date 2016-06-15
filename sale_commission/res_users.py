# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class User(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'sale_commission_rule_id': fields.many2one('sale.commission.rule',
                                                   string='Commission Rule'),
    }
