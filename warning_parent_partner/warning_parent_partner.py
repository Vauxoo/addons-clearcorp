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

from openerp import tools,models, fields, api,_
from openerp.tools.translate import _

class sale_order(models.Model):
    _inherit = 'sale.order'
    @api.v7
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part,context=context)
        if not result.get('warning'):
            warning = {}
            title = False
            message = False
            partner = self.pool.get('res.partner').browse(cr, uid, part, context=context)
            if partner.parent_id:
                if partner.parent_id.sale_warn != 'no-message':
                    title =  _("Warning for %s") % partner.name
                    message = partner.parent_id.sale_warn_msg
                    warning = {
                               'title': title,
                               'message': message,
                               }
                    if partner.parent_id.sale_warn == 'block':
                        return {'value': {'partner_id': False}, 'warning': warning}
                    if result.get('warning',False):
                        warning['title'] = title and title +' & '+ result['warning']['title'] or result['warning']['title']
                        warning['message'] = message and message + ' ' + result['warning']['message'] or result['warning']['message']
            if warning:
                result['warning'] = warning
        return result
class account_invoice(models.Model):
    _inherit = 'account.invoice'
    @api.v7
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                        date_invoice=False, payment_term=False,
                        partner_bank_id=False, company_id=False,
                        context=None):
        result =  super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
        date_invoice=date_invoice, payment_term=payment_term, 
        partner_bank_id=partner_bank_id, company_id=company_id, context=context)
        if not result.get('warning'):
            warning = {}
            title = False
            message = False
            if not partner_id:
                return {'value': {
                    'account_id': False,
                    'payment_term': False,
                }
            }
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if partner.parent_id:
                if partner.parent_id.invoice_warn != 'no-message':
                    title =  _("Warning for %s") % partner.name
                    message = partner.parent_id.sale_warn_msg
                    warning = {
                        'title': title,
                        'message': message,
                    }
                    if partner.parent_id.invoice_warn == 'block':
                        return {'value': {'partner_id': False}, 'warning': warning}
                    if result.get('warning',False):
                        warning['title'] = title and title +' & '+ result['warning']['title'] or result['warning']['title']
                        warning['message'] = message and message + ' ' + result['warning']['message'] or result['warning']['message']
            if warning:
                result['warning'] = warning
        return result
            
class purchase_order(models.Model):
    _inherit = 'purchase.order'
    @api.v7
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result =  super(purchase_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
        if not result.get('warning'):
            warning = {}
            title = False
            message = False
            partner = self.pool.get('res.partner').browse(cr, uid, part, context=context)
            if partner.parent_id:
                if partner.parent_id.purchase_warn != 'no-message':
                    title = _("Warning for %s") % partner.name
                    message = partner.parent_id.purchase_warn_msg
                    warning = {
                           'title': title,
                           'message': message
                           }
                    if partner.parent_id.purchase_warn == 'block':
                        return {'value': {'partner_id': False}, 'warning': warning}

                    if result.get('warning',False):
                        warning['title'] = title and title +' & '+ result['warning']['title'] or result['warning']['title']
                        warning['message'] = message and message + ' ' + result['warning']['message'] or result['warning']['message']
            if warning:
                result['warning'] = warning
        return result