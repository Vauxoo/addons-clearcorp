# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSummary(models.Model):

    _inherit = 'product.template'

    @api.one
    def action_recal_cost(self):
        for product in self:
            services = 0.0
            others = 0.0
            for materials in product.bom_ids:
                for line in materials.bom_line_ids:
                    if line.product_id.type == 'service':
                        services += line.product_qty * \
                                    line.product_id.standard_price
                    else:
                        others += line.product_qty * \
                                  line.product_id.standard_price
            if others+services > 0:
                product.cost_w_services = others+services
                product.cost_services = services
                product.standard_price = others

    @api.depends('standard_price', 'cost_services')
    def _compute_total(self):
        for product in self:
            product.cost_w_services = product.standard_price +\
                                      product.cost_services

    cost_w_services = fields.Float('Cost With Service',
                                   compute='_compute_total', readonly=True)
    cost_services = fields.Float('Cost Service')

