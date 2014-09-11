#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _

class ResCompany(osv.Model):
    
    _inherit = 'res.company'
    
    _columns = {
                'default_move_discount_id': fields.many2one('account.account',
                    string='Default Move Discount Account'),
                }

class ConfigSettings(osv.Model):
    
    _inherit = 'account.config.settings'
    
    _columns = {
                'default_move_discount_id': fields.related('company_id','default_move_discount_id',
                    type='many2one', relation='account.account', string='Default Move Discount Account'),
                }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(ConfigSettings, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({'default_move_discount_id': company.default_move_discount_id and company.default_move_discount_id.id or False})
        else: 
            res['value'].update({'default_move_discount_id': False})
        return res
    
class Invoice(osv.Model):
    
    _inherit = 'account.invoice'
    
    def action_move_create(self, cr, uid, ids, context=None):
        res = super(Invoice,self).action_move_create(cr, uid, ids, context=context)
        for invoice in self.browse(cr, uid, ids, context=context):
            #check invoice type
            if invoice.type in ['out_invoice','out_refund']:
                # check if invoice had discount
                if invoice.amount_discounted != 0.0:
                    
                    # Get default discount account from company
                    default_move_discount = invoice.company_id.default_move_discount_id and \
                    invoice.company_id.default_move_discount_id.id or False
                    if not default_move_discount:
                        raise osv.except_osv(_('Error'),_('No default move discount account configured for '
                                                          'company %s') % invoice.company_id.name)
                        
                    move_line_obj = self.pool.get('account.move.line')
                    
                    # Create values for new move line related to the invoice
                    values = {
                              'invoice': invoice.id,
                              'name': _('discount'),
                              'quantity': 1,
                              'debit': 0.0,
                              'credit': 0.0,
                              'account_id': default_move_discount,
                              'move_id': invoice.move_id.id,
                              'period_id': invoice.move_id.period_id.id,
                              'partner_id': invoice.partner_id.id,
                              'date_created': invoice.date_invoice,
                              'state': 'valid',
                              'date_maturity': invoice.move_id.date,
                              }
                    
                    
                    if invoice.type == 'out_invoice':
                        values['debit'] = invoice.amount_discounted
                    else: # for out_refund
                        values['credit'] = invoice.amount_discounted
                        
                    move_line_id = move_line_obj.create(cr, uid, values, context=context)
                    
                    for invoice_line in invoice.invoice_line:
                        
                        values = {
                              'invoice': invoice.id,
                              'name': _('discount') + ' ' + invoice_line.name,
                              'quantity': invoice_line.quantity,
                              'debit': 0.0,
                              'credit': 0.0,
                              'account_id': invoice_line.account_id.id,
                              'move_id': invoice.move_id.id,
                              'period_id': invoice.move_id.period_id.id,
                              'partner_id': invoice.partner_id.id,
                              'date_created': invoice.date_invoice,
                              'state': 'valid',
                              }
                        
                        if invoice.type == 'out_invoice':
                            values['credit'] = (invoice_line.quantity * invoice_line.price_unit) - \
                            invoice_line.price_subtotal
                        else: # for out_refund
                            values['debit'] = (invoice_line.quantity * invoice_line.price_unit) - \
                            invoice_line.price_subtotal
                        
                        move_line_id = move_line_obj.create(cr, uid, values, context=context)