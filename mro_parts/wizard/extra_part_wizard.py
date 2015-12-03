from openerp import models, fields, api, _

class ExtraPart(models.TransientModel):
    
    _name = 'mro.parts.extra.parts'

    parts_extra_lines = fields.Many2many('mro.order.parts.line.extra', string='Extra Parts')
    maintenance_id = fields.Many2one('mro.order', string='Maintenance Order', select=True)
    
    @api.multi
    def add_extra_parts(self):
        proc_ids=[]
        procurement_obj = self.env['procurement.order']
        part_line_obj = self.env['mro.order.parts.line']
        active_ids = self._context.get('active_ids', [])
        mro_order = self.env['mro.order'].search([('id','=',active_ids[0])])
        for line in self.parts_extra_lines:
                vals = {
                    'name': mro_order.name + _(' -Extra'),
                    'origin': mro_order.name + _(' -Extra'),
                    'company_id': mro_order.company_id.id,
                    'group_id': mro_order.procurement_group_id.id,
                    'date_planned': mro_order.date_planned,
                    'product_id': line.parts_id.id,
                    'product_qty': line.parts_qty,
                    'product_uom': line.parts_uom.id,
                    'location_id': mro_order.asset_id.property_stock_asset.id
                    }
                proc_id = procurement_obj.create(vals)
                proc_ids.append(proc_id.id)
                vals_line = {
                    'parts_id': line.parts_id.id,
                    'parts_qty': line.parts_qty,
                    'product_uom': line.parts_uom.id,
                    'maintenance_id': line.maintenance_id.id
                    }
                part_line = part_line_obj.create(vals_line)
                
        procurement_obj.browse(proc_ids).run()
        return 0
        