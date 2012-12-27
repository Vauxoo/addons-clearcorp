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



class sale_commission(osv.osv):
    def write(self, cr, uid, ids, vals, context=None):
        res = []
        invoices_id = []
        nc_id = []
        commission_total = 0
        total_paid = 0
        total_nc = 0
        total_all = 0
        today = datetime.now().strftime('%Y-%m-%d')
        voucher_obj = self.pool.get('account.voucher')
        part_obj = self.pool.get('res.partner')
        user_obj = self.pool.get('res.user')
        inv_all_obj = self.pool.get('account.invoice')
        inv_paid_obj = self.pool.get('account.invoice')
        inv_expiry_obj = self.pool.get('account.invoice')
        inv_nc_obj = self.pool.get('account.invoice')
        res = super(sale_commission, self).write(cr, uid, ids, vals, context=context)

        for commission in self.browse(cr, uid, ids, context=context):

            # Facturas Vencidas
            inv_expiry_obj = commission.account_invoice_expiry_id

            for inv in inv_expiry_obj:
                if inv.currency_id.id == inv.company_id.currency_id.id:
                    rate = 1
                else:
                    rate = inv.currency_id.rate * inv.company_id.currency_id.rate

                total_all = total_all + (inv.amount_untaxed * rate)



            # Facturas pagadas

            inv_paid_obj = commission.account_invoice_paid_id

            for inv in inv_paid_obj:


                if inv.currency_id.id == inv.company_id.currency_id.id:
                    rate = 1
                else:
                    rate = inv.currency_id.rate * inv.company_id.currency_id.rate


                if not inv.id in invoices_id:
                    invoices_id.append(inv.id)
                    total_paid = total_paid + (inv.amount_untaxed * rate)
                    commission_total = commission_total + (inv.amount_untaxed * rate * inv.partner_id.commission)



            # Notas de credito
            inv_nc_obj = commission.account_invoice_nc_id

            for inv in inv_nc_obj:
                if inv.currency_id.id == inv.company_id.currency_id.id:
                    rate = 1
                else:
                    rate = inv.currency_id.rate * inv.company_id.currency_id.rate


                if not inv.id in nc_id:
                    nc_id.append(inv.id)
                    total_nc = total_nc + (inv.amount_untaxed * rate)
                    commission_total = commission_total - (inv.amount_untaxed * rate * inv.partner_id.commission)


            vals['total_sale'] = total_all + total_paid
            vals['total_sale_paid'] = total_paid
            vals['total_nc'] = total_nc
            vals['total_pay'] = commission_total
        res = super(sale_commission, self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        res = []
        invoices_id = []
        nc_id = []
        commission = 0
        total_paid = 0
        total_nc = 0
        total_all = 0
        today = datetime.now().strftime('%Y-%m-%d')
        voucher_obj = self.pool.get('account.voucher')
        part_obj = self.pool.get('res.partner')
        user_obj = self.pool.get('res.user')
        inv_all_obj = self.pool.get('account.invoice')
        inv_paid_obj = self.pool.get('account.invoice')
        inv_expiry_obj = self.pool.get('account.invoice')
        inv_nc_obj = self.pool.get('account.invoice')
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.commission')

        # Facturas Ventas
        inv_all_obj = inv_all_obj.search(cr, uid, [('date_invoice','<',vals['commission_end']),('date_invoice','>',vals['commission_start']),('user_id','=',vals['user_id']),('state','in',('paid','open','cancel')),('type','=','out_invoice')], context=context)

        for inv in inv_all_obj:
            inv = self.pool.get('account.invoice').browse(cr, uid, inv, context=context)
            if inv.currency_id.id == inv.company_id.currency_id.id:
                rate = 1
            else:
                rate = inv.currency_id.rate * inv.company_id.currency_id.rate

            total_all = total_all + (inv.amount_untaxed * rate)



        # Facturas pagadas
        inv_paid_obj = inv_paid_obj.search(cr, uid, [('date_invoice','<',vals['commission_end']),('date_invoice','>',vals['commission_start']),('user_id','=',vals['user_id']),('state','=','paid'),('type','=','out_invoice')], context=context)

        for inv in inv_paid_obj:
            inv = self.pool.get('account.invoice').browse(cr, uid, inv, context=context)

            if inv.currency_id.id == inv.company_id.currency_id.id:
                rate = 1
            else:
                rate = inv.currency_id.rate * inv.company_id.currency_id.rate


            if not inv.id in invoices_id:
                invoices_id.append(inv.id)
                total_paid = total_paid + (inv.amount_untaxed * rate)
                commission = commission + (inv.amount_untaxed * rate * inv.partner_id.commission)



        # Notas de credito
        inv_nc_obj = inv_nc_obj.search(cr, uid, [('date_invoice','<',vals['commission_end']),('date_invoice','>',vals['commission_start']),('user_id','=',vals['user_id']),('state','=','paid'),('type','=','out_refund')], context=context)

        for inv in inv_nc_obj:
            inv = self.pool.get('account.invoice').browse(cr, uid, inv, context=context)
            if inv.currency_id.id == inv.company_id.currency_id.id:
                rate = 1
            else:
                rate = inv.currency_id.rate * inv.company_id.currency_id.rate


            if not inv.id in nc_id:
                nc_id.append(inv.id)
                total_nc = total_nc + (inv.amount_untaxed * rate)
                commission = commission - (inv.amount_untaxed * rate * inv.partner_id.commission)


        # Facturas Vencidas
        inv_expiry_obj = inv_expiry_obj.search(cr, uid, [('date_invoice','<',vals['commission_end']),('date_invoice','>',vals['commission_start']),('user_id','=',vals['user_id']),('state','=','open'),('type','=','out_invoice')], context=context)

        vals['total_sale'] = total_all
        vals['total_sale_paid'] = total_paid
        vals['account_invoice_paid_id'] = [[6,0,invoices_id]]
        vals['total_nc'] = total_nc
        vals['account_invoice_nc_id'] = [[6,0,nc_id]]
        vals['total_pay'] = commission
        vals['account_invoice_expiry_id'] = [[6,0,inv_expiry_obj]]


        res= super(sale_commission, self).create(cr, uid, vals, context=context)
        return res
    def action_set_invoice_commision(self, cr, uid, ids, context=None):
        res = {}
        for comm in self.browse(cr, uid, ids):
            for inv in comm.account_invoice_paid_id:
                inv.write({'commision_paid': True}, context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    _name = "sale.commission"
    _columns = {
        'name': fields.char('Nombre',size=64,readonly=True),
        'total_pay': fields.float('Comision', readonly=True),
        'total_nc': fields.float('Total NC', readonly=True),
        'total_sale_paid': fields.float('Total Pagas', readonly=True),
        'total_sale': fields.float('Total Ventas', readonly=True),
        'commission_start' : fields.date('Fecha Inicio', required=True),
        'commission_end' : fields.date('Fecha Fin', required=True),
        'create_date' : fields.datetime('Fecha Creacion', readonly=True),
        'user_id': fields.many2one('res.users', 'Vendedor', required=True),
        'account_invoice_paid_id': fields.many2many('account.invoice', 'commision_invoice_paid_id', 'sale_commission_id', 'invoice_id', 'Facturas Pagadas'),
        'account_invoice_expiry_id': fields.many2many('account.invoice', 'commision_invoice_expiry_id', 'sale_commission_id', 'invoice_id', 'Facturas Vencidas'),
        'account_invoice_nc_id': fields.many2many('account.invoice', 'commision_invoice_nc_id', 'sale_commission_id', 'invoice_id', 'Notas Credito'),
        'state': fields.selection([('draft', 'Borrador'), ('confirmed', 'Confirmado'), ('done', 'Procesado'), ('cancel', 'Cancelado')], 'Estado', required=True, readonly=True)
    }
    _defaults = {
        'state': lambda *args: 'draft',
    }
sale_commission()
