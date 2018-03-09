# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp import tools


class StockMoveAnalysis(models.Model):

    _name = 'stock.move.analysis'
    _description = 'Stock Move Analysis'
    _auto = False

    date = fields.Datetime('Date', readonly=True)
    origin = fields.Char('Description', readonly=True)
    name = fields.Char('Name', readonly=True)
    product_id = fields.Many2one(
        'product.product', 'Product', readonly=True)
    categ_id = fields.Many2one(
        'product.category', string='Category Product', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Company', readonly=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type', readonly=True)
    location_src_id = fields.Many2one(
        'stock.location', 'Source Location', readonly=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location', readonly=True)
    product_qty = fields.Float(
        'Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
        readonly=True)
    standard_price = fields.Float(
        'Standard Price', digits_compute=dp.get_precision('Account'),
        readonly=True)
    total = fields.Float(
        'Total', digits_compute=dp.get_precision('Account'), readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_move_analysis')
        cr.execute("""
create or replace view stock_move_analysis as (
  select
    ROW_NUMBER() OVER() AS id,
    stm.date as date,
    stm.origin as origin,
    stm.name as name,
    stm.product_id as product_id,
    pt.categ_id as categ_id,
    stm.partner_id as partner_id,
    stm.picking_type_id as picking_type_id,
    stm.location_id as location_src_id,
    stm.location_dest_id as location_dest_id,
    sum(stm.product_qty) as product_qty,
    coalesce((
      select sum(abs(sq.qty)*sq.cost)/sum(abs(sq.qty)) from stock_quant sq
    left join stock_quant_move_rel sqm on (sq.id=sqm.quant_id)
    left join stock_move smo on (sqm.move_id=smo.id)
    where smo.id=stm.id),0) as standard_price,
    coalesce((sum(stm.product_qty)*(
      select sum(abs(sq.qty)*sq.cost)/sum(abs(sq.qty)) from stock_quant sq
    left join stock_quant_move_rel sqm on (sq.id=sqm.quant_id)
    left join stock_move smo on (sqm.move_id=smo.id)
    where smo.id=stm.id)),0) as total
  from
    stock_move stm
    left join product_product p on (stm.product_id = p.id)
    left join product_template pt on (p.product_tmpl_id = pt.id)
  group by stm.id, stm.date, stm.origin, stm.name,
    stm.product_id, stm.location_id, stm.location_dest_id,
    pt.categ_id order by stm.date)""")
