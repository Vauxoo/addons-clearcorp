# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class SuggestedProdutList(models.Model):

    _inherit = 'product.template'

    @api.one
    def _compute_list_product(self):
        self._cr.execute("""SELECT id FROM (SELECT pt.id,
                        SUM(o.product_uom_qty) AS qty FROM product_template pt,
                        product_product p, sale_order s,sale_order_line o
                        WHERE s.id=o.order_id AND o.product_id=p.id
                        AND s.state in ('sale','done') AND
                        s.id IN (SELECT s.id FROM  product_product p,
                                sale_order
                                s,sale_order_line o
                                WHERE s.state in ('sale','done')
                                AND s.id=o.order_id
                                AND o.product_id=p.id
                                AND p.product_tmpl_id=%s) AND
                        s.date_order>=(current_date -90) AND
                        pt.id=p.product_tmpl_id AND pt.id<>%s GROUP BY pt.id
                        ORDER BY qty DESC LIMIT %s) AS det;""",
                         (self.id, self.id,
                          self.env.user.company_id.bought_product_limit,))
        related_recordset = \
            self.env["product.template"].search([("id",
                                                "=",
                                                 self._cr.fetchall())])
        self.product_list = related_recordset

    product_list = fields.One2many('product.template',
                                   string="Suggested product",
                                   compute='_compute_list_product')
