from openerp import models, fields, api, _

class SaleOrderWizard(models.TransientModel):
    
    _name = 'sale.order.wizard'
    
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    
    @api.multi
    def generate_saleorder(self):
        feature = self.env['ccorp.project.scrum.feature']
        data = self._context.get('active_ids', [])
        feat = feature.search([('id','in',data)])
        res = feat.generate_so(feat, self.sale_order_id)
        return res