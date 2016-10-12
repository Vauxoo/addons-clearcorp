# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class SetingssuggestProduct(models.TransientModel):

    _inherit = 'sale.config.settings'

    bought_product_limit = fields.Float('Suggested Products Display',
                                        digits_compute=0,
                                        help='Max suggested products to be display.')

    def get_default_bought_product_limit(self, cr, uid, fields, context=None):
        """Get the default company bought_product_limit"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid,
                                                      'sale.cofig', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'bought_product_limit': company.bought_product_limit}

    def set_bought_product_limit(self, cr, uid, ids, context=None):
        """Set the new bought_product_limit in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid,
                                                      'sale.cofig', context=context)
        company_obj.write(cr, uid, company_id,
                          {'bought_product_limit': config.bought_product_limit},
                          context=context)
