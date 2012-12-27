from osv import osv, fields
import decimal_precision as dp
import math
import logging
import re
from tools.translate import _

class purchase_import_voucher(osv.osv):
    def _calc_amount_cif(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for voucher in self.browse(cr, uid, ids):
            res[voucher.id] = voucher.order_id.total_products +  voucher.order_id.total_freight
        return res
    def _calc_amount_cif_dolars(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for voucher in self.browse(cr, uid, ids):
            res[voucher.id] = voucher.currency_rate * voucher.cif_real
        return res

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    _name = 'purchase.import.voucher'
    _columns = {
        'name': fields.char('Number',size=64),
        'date_voucher' : fields.datetime('Create Date'),
        'location_id' : fields.many2one('res.partner.address', 'Origin'),
        'bidder_id' : fields.many2one('res.partner', 'Bidder'),
        'agent_number': fields.char('Agent Number',size=64),
        'state_voucher': fields.char('State',size=64),
        'regime': fields.char('Regime',size=64),
        'importexport': fields.char('Import/Export',size=64),
        'mode': fields.char('Mode',size=64),
        'type_audit': fields.char('Audit Type',size=64),
        'num_bags': fields.float('Bag Number'),
        'weight': fields.float('Weight'),
        'weight_net': fields.float('Weight Net'),
        'cif_real': fields.function(_calc_amount_cif, method=True, string='CIF Real', type='float',help='Cost, insurance, freight'),
        'cif_paid': fields.float('CIF Paid', required=True),
        'cif_dolars': fields.function(_calc_amount_cif_dolars, method=True, string='CIF USD', type='float',help='(Cost, insurance, freight)* Currency Rate'),
        'currency_rate': fields.float('Currency Rate'),
        'tax': fields.related('tax_order_id','order_line',type='one2many',relation='purchase.order.line',string='Currency', store=False),
        'order_id': fields.many2one('purchase.import.order', 'Order',ondelete='set null', select=True),
    }
    _defaults = {
    }
purchase_import_voucher()

class purchase_import_order(osv.osv):
    def create(self, cr, uid, vals, context=None):
        res = []
        line_ids = []
        inv_obj = self.pool.get('account.invoice')
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.import.order')
        invoices = vals['imports_order_id']

        for inv in inv_obj.browse(cr, uid, invoices[0][2]):
            for line in inv.invoice_line:
                line_ids.append(line.id)

        vals['lines_id'] = [[6,False,line_ids]]

        res= super(purchase_import_order, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res =[]
        line_ids = []
        inv_obj = self.pool.get('account.invoice')
        if 'imports_order_id' in vals:
            invoices = vals['imports_order_id']
            for inv in inv_obj.browse(cr, uid, invoices[0][2]):
                for line in inv.invoice_line:
                    line_ids.append(line.id)
            vals['lines_id'] = [[6,False,line_ids]]

        res = super(purchase_import_order, self).write(cr, uid, ids, vals, context=context)
        return res

    def _calc_amount_total(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for order in self.browse(cr, uid, ids):
            res[order.id] = order.tax_total+ order.total_freight
        return res

    def _calc_amount_tax(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for order in self.browse(cr, uid, ids):
            if order.tax_order_id:
                if order.tax_order_id.currency_id.id == order.tax_order_id.company_id.currency_id.id:
                    currency = 1
                else:
                    currency = order.tax_order_id.currency_id.rate * order.tax_order_id.company_id.currency_id.rate
                res[order.id] = order.tax_order_id.amount_untaxed * currency

            else:
                res[order.id] = 0
        return res
    def _calc_amount_prod(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        total = 0
        for imports in self.browse(cr, uid, ids):
            for order in imports.imports_order_id:
                if order.currency_id.id == order.company_id.currency_id.id:
                    currency = 1
                else:
                    currency = order.currency_id.rate * order.company_id.currency_id.rate
                total = total + (order.amount_untaxed * currency)

            res[imports.id] = total
        return res

    def _calc_amount_freight(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for order in self.browse(cr, uid, ids):
            if order.freight_order_id:
                if order.freight_order_id.currency_id.rate == order.freight_order_id.company_id.currency_id.rate:
                    currency = 1
                else:
                    currency = order.freight_order_id.currency_id.rate * order.freight_order_id.company_id.currency_id.rate

                res[order.id] = (order.freight_order_id.amount_untaxed + order.fob) * currency
            else:
                res[order.id] = 0
        return res
    def _calc_amount_insurance(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for order in self.browse(cr, uid, ids):
            if order.insurance_order_id:
                if order.insurance_order_id.currency_id.rate == order.insurance_order_id.company_id.currency_id.rate:
                    currency = 1
                else:
                    currency = order.insurance_order_id.currency_id.rate * order.insurance_order_id.company_id.currency_id.rate

                res[order.id] = order.insurance_order_id.amount_untaxed * currency
            else:
                res[order.id] = 0
        return res

    def action_set_average_price(self, cr, uid, ids, context=None):
        res = {}
        total_weight = 0
        order_tax = 0
        product_freight = 0
        product_tax = 0
        product_insurance  = 0

        for imports in self.browse(cr, uid, ids):
            if imports.cif_paid == 0:
                raise osv.except_osv(_('Invalid Document!'), _('Update CiF Cost" '))

            if imports.tax_order_id:
                if imports.tax_order_id.currency_id.id == imports.tax_order_id.company_id.currency_id.id:
                    tax_currency_rate = 1
                else:
                    tax_currency_rate = imports.tax_order_id.currency_id.rate * imports.tax_order_id.company_id.currency_id.rate


            for line in imports.lines_id:
                uos_ratio = 1
                if line.uos_id.uom_type =='reference':
                        uos_ratio = 1
                else:
                    if line.uos_id.uom_type =='bigger':
                        uos_ratio = line.uos_id.factor_inv
                    else:
                        uos_ratio = line.uos_id.factor
                line_qty = line.quantity * uos_ratio

                product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
                total_weight = total_weight + (line_qty * product.weight)
                order_tax = order_tax + product.tax_total

                if (line_qty * product.weight) <= 0:
                    raise osv.except_osv(_('Product with weight 0 !'), _('Update the product with part number "%s" ') % (product.part_number))

                if (line_qty * product.tax_total) <= 0:
                    raise osv.except_osv(_('Product without tariff !'), _('Update the product with part number  "%s" ') % (product.part_number))

            for order in imports.imports_order_id:
                if order.currency_id.id == order.company_id.currency_id.id:
                    import_currency_rate = 1
                else:
                    import_currency_rate = order.currency_id.rate * order.company_id.currency_id.rate

                for line in order.invoice_line:
                    if line.uos_id.uom_type =='reference':
                        uos_ratio = 1
                    else:
                        if line.uos_id.uom_type =='bigger':
                            uos_ratio = line.uos_id.factor_inv
                        else:
                            uos_ratio = line.uos_id.factor
                    line_qty = line.quantity * uos_ratio


                    product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)

                    #Update price per weight
                    if imports.freight_order_id:
                        product_freight_percentage = product.weight * line_qty / total_weight
                        product_freight = imports.total_freight * product_freight_percentage / line_qty

                    #Update price per taxes
                    if imports.tax_order_id:
                        product_tax_percentage = product.tax_total / order_tax
                        product_tax= imports.tax_total * product_tax_percentage / line_qty




                    add_cost = (line.price_unit/ uos_ratio * import_currency_rate) + product_freight + product_tax + product_insurance

                    if product.qty_available <= line_qty:
                        cost = add_cost
                    else:
                        cost = (add_cost * line_qty  + product.standard_price * (product.qty_available - line_qty))/ product.qty_available

                    product.write({'costo_fob': line.price_unit}, context=context)
                    product.write({'standard_price': cost}, context=context)

        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    _name = 'purchase.import.order'
    _columns = {
        'name': fields.char('Number',size=64,readonly=True),
        'fob': fields.float('FoB', required=True),

        'voucher_id': fields.one2many('purchase.import.voucher', 'order_id', 'Voucher'),
        'provenance_id' : fields.many2one('res.country', 'Origin',required=True),


        'imports_order_id': fields.many2many('account.invoice', 'import_invoice_id', 'imports_id', 'invoice_id', 'Product Invoices'),

        'freight_order_id':fields.many2one('account.invoice', 'Freight Invoice'),
        'tax_order_id':fields.many2one('account.invoice', 'Tax Invoice'),

        'date_arrive' : fields.datetime('Land Date'),
        'date_due' : fields.datetime('Due Date'),

        'total_products': fields.function(_calc_amount_prod, method=True, string='Product total', type='float'),

        'tax_total': fields.function(_calc_amount_tax, method=True, string='Tax Total', type='float'),
        'total_freight': fields.function(_calc_amount_freight, method=True, string='Freight Total', type='float'),
        'total_paid': fields.function(_calc_amount_total, method=True, string='Import Total', type='float'),

        'lines_id': fields.many2many('account.invoice.line', 'import_line_id', 'imports_id', 'line_id', 'Products',readonly=True),

        'freight': fields.related('freight_order_id','invoice_line',type='one2many',relation='account.invoice.line',string='Freight', store=False),
        'freight_currency': fields.related('freight_order_id','currency_id',type='many2one',relation='res.currency',string='Freight Currency', store=False),

        'taxes': fields.related('tax_order_id','invoice_line',type='one2many',relation='account.invoice.line',string='Taxes', store=False),
        'taxes_currency': fields.related('tax_order_id','currency_id',type='many2one',relation='res.currency',string='Tax Currency', store=False),


        'cif_paid': fields.related('voucher_id', 'cif_paid', type='float', string='CIF Paid'),
        'cif_real': fields.related('voucher_id', 'cif_real', type='float', string='CIF Real'),

        'note': fields.text('Notes'),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancel')], 'State', required=True, readonly=True)
    }
    _defaults = {
        'state': lambda *args: 'draft',
    }

purchase_import_order()

