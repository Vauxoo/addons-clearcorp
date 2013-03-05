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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from osv import osv, fields
import netsvc
import pooler
from tools.translate import _
import decimal_precision as dp
from osv.orm import browse_record, browse_null
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class ccorp_purchase_order_archive(osv.osv):
    #Customization for purchase.order adding "archived" state and performing workflow operations for this new state.
    _inherit = 'purchase.order'
    
    STATE_SELECTION = [
        ('draft', 'Request for Quotation'),
        ('wait', 'Waiting'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('archived', 'Archived')
    ]
    
    _columns ={
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, 
        help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
        
        }
        
        #Cancel the order and put it into archived status 
    def action_archive(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for purchase in self.browse(cr, uid, ids, context=context):
            for pick in purchase.picking_ids:
                if pick.state not in ('draft','cancel'):
                    raise osv.except_osv(
                        _('Unable to archive this purchase order!'),
                        _('You must first cancel all receptions related to this purchase order.'))
            for pick in purchase.picking_ids:
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
            for inv in purchase.invoice_ids:
                if inv and inv.state not in ('cancel','draft'):
                    raise osv.except_osv(
                        _('Unable to archive this purchase order!'),
                        _('You must first cancel all invoices related to this purchase order.'))
                if inv:
                    wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
        
        for (id, name) in self.name_get(cr, uid, ids):
            wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)
            message = _("Purchase order '%s' is archived.") % name
            self.log(cr, uid, id, message)
        self.write(cr,uid,ids,{'state':'archived'})
        return True
    
        #Overwrites the unlink, disabling the option of delete the order once archived 
    def unlink(self, cr, uid, ids, context=None):
        purchase_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in purchase_orders:
            if s['state'] in ['draft','cancel']:
                unlink_ids.append(s['id'])
            if s['state'] in ['archived']:
                raise osv.except_osv(_('Invalid action !'), _('An archived purchase order cannot be deleted!'))
            else:
                raise osv.except_osv(_('Invalid action !'), _('In order to delete a purchase order, it must be cancelled first!'))

        # TODO: temporary fix in 5.0, to remove in 5.2 when subflows support
        # automatically sending subflow.delete upon deletion
        wf_service = netsvc.LocalService("workflow")
        for id in unlink_ids:
            wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)

        return super(ccorp_purchase_order_archive, self).unlink(cr, uid, unlink_ids, context=context)
    
    #Overwrites the write, disabling the option of modify the order once archived
    def write(self, cr, uid, ids, vals, context=None):
        purchase_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in purchase_orders:
            if s['state'] in ['archived']:
                raise osv.except_osv(_('Invalid action !'), _('An archived purchase order cannot be edited!'))       
        return super(ccorp_purchase_order_archive, self).write(cr, uid, ids, vals, context=context)
    
