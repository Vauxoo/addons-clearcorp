# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp import tools

class extendedAssetReport(osv.Model):
    
    _name = 'asset.asset.report.extended'
    _description = 'Asset Analysis Extended '
    _auto = False # Do not create table automatically
    
    _columns = _columns = {
                           'invoice_id': fields.many2one('account.invoice', string='Invoice'),
                           'name': fields.char('Asset Name', size=64),
                           'asset_id': fields.many2one('account.asset.asset', string='Asset'),
                           'asset_category_id': fields.many2one('account.asset.category', string='Asset Category'),
                           'model': fields.char('Model', size=64),
                           'asset_number': fields.char('Asset Number', size=64),
                           'supplier_id': fields.many2one('res.partner', string='Supplier'),
                           'gross_value': fields.float('Gross Amount', readonly=True),
                           'salvage_value': fields.float('Salvage Amount', readonly=True),
                           'depreciation': fields.float('Depreciation', readonly=True),
                           'value_residual': fields.float('Residual Value', readonly=True),
                           'responsible_id': fields.many2one('res.partner', string='Responsible'),
                           }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'asset_asset_report_extended')
        cr.execute("""CREATE OR REPLACE VIEW asset_asset_report_extended AS
(SELECT
  asset.id,
  (CASE WHEN
    asset.account_invoice_line_id IS NOT NULL
  THEN
   (SELECT
     invoice.id
   FROM
     account_invoice AS invoice,
     account_invoice_line AS line
   WHERE
    line.id = asset.account_invoice_line_id AND
    line.invoice_id = invoice.id
   )
   ELSE
     NULL
   END
  ) AS invoice_id,
  asset.name,
  asset.id AS asset_id,
  asset.category_id AS asset_category_id,
  asset.model,
  asset.asset_number,
  (CASE WHEN
    asset.account_invoice_line_id IS NOT NULL
  THEN
   (SELECT
     b.partner_id
   FROM
     account_asset_asset AS a,
     account_invoice_line AS b
   WHERE
    a.account_invoice_line_id = b.id AND
    a.id = asset.id
   )
   ELSE
     NULL
   END
  ) AS supplier_id,
  (CASE WHEN
    (SELECT
      dp.remaining_value
    FROM
      account_asset_depreciation_line AS dp
    WHERE
      dp.asset_id = asset.id AND
      dp.move_check = TRUE
    ORDER BY
      dp.sequence DESC
    LIMIT 1) IS NOT NULL
  THEN
    (SELECT
      dp.remaining_value
    FROM
      account_asset_depreciation_line AS dp
    WHERE
      dp.asset_id = asset.id AND
      dp.move_check = TRUE
    ORDER BY
      dp.sequence DESC
    LIMIT 1)
  ELSE
    asset.purchase_value
  END) AS value_residual,
  asset.purchase_value AS gross_value,
  asset.salvage_value,
  (SELECT
    SUM(dp.amount)
  FROM
    account_asset_depreciation_line as dp
  WHERE
    dp.asset_id = asset.id AND
    dp.move_check = TRUE) AS depreciation,
  asset.responsible AS responsible_id 
FROM 
  account_asset_asset AS asset)""")
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: