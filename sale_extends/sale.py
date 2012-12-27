from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import pooler
from osv import fields, osv
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import logging



class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'name': fields.char('Order Reference', size=64, required=True,readonly=True),
        'local': fields.boolean('Local'),
        'oc': fields.binary('Data'),
        'credit_app': fields.boolean('Credit Aprove'),
        'validez': fields.selection([
            ('7', '7 Days'),
            ('15', '15 Days'),
            ('30', '30 Days'),
            ('45', '45 Days'),
        ], 'Validity', required=True),
        'create_user_id': fields.many2one('res.users', 'Create by', readonly=True),
    }
    _defaults = {
        'create_user_id': lambda obj, cr, uid, context: uid,
    }
    def action_wait(self, cr, uid, ids, context=None):
        due_invoice= []
        inv_obj = self.pool.get('account.invoice')
        today = datetime.now().strftime('%Y-%m-%d')

        for order in self.pool.get('sale.order').browse(cr, uid, ids,context=context):
            partner = order.partner_id
            due_invoices = inv_obj.search(cr, uid, [('date_due','<',today),('partner_id','=',partner.id),('state','=','open'),('type','=','out_invoice')], context=context)
            if order.payment_term.credit:
                if not order.credit_app:
                    if (partner.credit + order.amount_total) > partner.credit_limit:
                        raise osv.except_osv(_('Invalid Order!'), _('Customer has no credit'))
                    if len(due_invoices)>0:
                        raise osv.except_osv(_('Invalid Order!'), _('customer with overdue bills'))
            if not order.client_order_ref:
                raise osv.except_osv(_('Invalid Order!'), _('Add a client purchase order or customer reference.'))
        res = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        return res

sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'part_number': fields.char('Part Number', size=64),
        'delivery_time': fields.char('Delivery Time', size=64, required=True),
    }
    _defaults = {
        'delivery_time': '1 day',
    }
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        product_obj = self.pool.get('product.product').browse(cr, uid, product,context=context)

        if 'name' in res['value']:
            res['value']['part_number']=product_obj.part_number
            if product_obj.qty_available >0:
                res['value']['product_uom_qty']=product_obj.virtual_available
            else:
                res['value']['product_uom_qty']=1
        return res
sale_order_line()
