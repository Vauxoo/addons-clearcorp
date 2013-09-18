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

from osv import osv,fields

class AccountAssetAsset(osv.osv):

    _inherit = 'account.asset.asset'
    _columns = {
        'account_invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line'),
        'account_invoice_id': fields.related('account_invoice_line_id', 'invoice_id', type="many2one", relation="account.invoice", string="Invoice", store=False),
        'responsible' : fields.many2one('res.partner', 'Responsible'),
        'model': fields.char('Model', size=64),
        'asset_number': fields.char('Asset Number', size=64),
    }

class AccountInvoiceLine(osv.osv):

    _inherit = 'account.invoice.line'
    _columns = {
        'asset_ids': fields.one2many('account.asset.asset', 'account_invoice_line_id', 'Asset', readonly=True, states={'draft':[('readonly',False)]}),
    }
    def asset_create(self, cr, uid, lines, context=None):
        context = context or {}
        asset_obj = self.pool.get('account.asset.asset')
        for line in lines:
            if line.asset_category_id:
                quantity = line.quantity
                cont = 1
                while cont <= quantity:
                    vals = {
                        'name': line.name,
                        'code': line.invoice_id.number or False,
                        'category_id': line.asset_category_id.id,
                        'purchase_value': line.price_subtotal/quantity,
                        'period_id': line.invoice_id.period_id.id,
                        'partner_id': line.invoice_id.partner_id.id,
                        'company_id': line.invoice_id.company_id.id,
                        'currency_id': line.invoice_id.currency_id.id,
                        'purchase_date' : line.invoice_id.date_invoice,
                    }
                    changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'], context=context)
                    vals.update(changed_vals['value'])
                    vals.update({'account_invoice_line_id': line.id})
                    asset_id = asset_obj.create(cr, uid, vals, context=context)
                    if line.asset_category_id.open_asset:
                        asset_obj.validate(cr, uid, [asset_id], context=context)
                    cont+=1
        return True
        
    def copy_data(self, cr, uid, id, default=None, context=None):
        res = super(AccountInvoiceLine, self).copy_data(cr, uid, id, default=default, context=context)
        res.update({
            'asset_ids': [],
        })
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
