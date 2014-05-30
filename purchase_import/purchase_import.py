# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Original Module by SIESA (<http://www.siesacr.com>)
#    Refactored by CLEARCORP S.A. (<http://clearcorp.co.cr>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from datetime import date, datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class ProductImportHistory(osv.Model):
    """Product Import History"""

    _name = 'purchase.import.product.import.history'
    
    _description = __doc__

    _columns = {
        'name': fields.char('Number', size=128, readonly=True),
        'import_number': fields.char('Import Number', size=128, readonly=True),
        'date' : fields.datetime('Date', readonly=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True),
        'last_price': fields.float('Last Price', readonly=True),
        'tax_percentage': fields.float('Tax (%)', readonly=True),
        'tax_total': fields.float('Total Taxes', readonly=True),
        'freight_percentage': fields.float('Freight (%)', readonly=True),
        'freight_total': fields.float('Freight Total', readonly=True),
        'import_total': fields.float('Import Cost', readonly=True),
    }

class TariffCategory(osv.Model):
    """Tariff Categories"""

    _name = 'purchase.import.tariff.category'

    _description = __doc__

    _order = 'code asc'

    _columns = {
        'code': fields.char('Code', size=32, required=True),
        'name': fields.char('Name', size=128, required=True),
        'description': fields.text('Description'),
    }

class Tax(osv.Model):
    """Taxes"""

    _name = 'purchase.import.tax'

    _description = __doc__

    _order = 'code asc'

    _columns = {
        'code': fields.char('Code', size=32, required=True),
        'name': fields.char('Tax Name', size=128, required=True),
        'value': fields.float('Tax Percentage', required=True),
        'tariff_id' : fields.many2one('purchase.import.tariff', string='Tariff'),
    }

class Tariff(osv.Model):
    """Import Tariffs"""

    _name = 'purchase.import.tariff'

    _description = __doc__

    def _compute_tariff_total(self, cr, uid, ids, field_name, arg, context=None):
        """Compute total taxes
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for tariff in self.browse(cr, uid, ids):
            total_tax = 0.0
            # Sum value from all related taxes
            for tax in tariff.tax_ids:
                total_tax += tax.value
            res[tariff.id] = total_tax
        return res

    _columns = {
        'name': fields.char('Tariff Name', size=128, required=True),
        'description': fields.text('Description'),
        'category_id' : fields.many2one('purchase.import.tariff.category', 'Category'),
        'tax_ids': fields.one2many('purchase.import.tax', 'tariff_id', 'Tax'),
        'tariff_total': fields.function(_compute_tariff_total, string='Total Taxes', type='float',help='Total Taxes from import'),
    }

class ImportOrderLine(osv.Model):
    """Import Order Lines"""

    _name = 'purchase.import.import.order.line'

    _description = __doc__

    def _compute_import_taxes(self, cr, uid, ids, field_name, arg, context=None):
        """Compute import taxes
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.subtotal * (line.tariff / 100)
        return res

    def _compute_tax_percentage(self, cr, uid, ids, field_name, arg, context=None):
        """Compute tax percentage
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.order_id.sum_tax_value:
                res[line.id] = (line.import_taxes / line.order_id.sum_tax_value) * 100
            else:
                res[line.id] = 0.0
        return res

    def _compute_tax_assigned(self, cr, uid, ids, field_name, arg, context=None):
        """Compute tax assigned
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.order_id.tax_total * line.tax_percentage) / 100
        return res

    def _compute_freight_percentage(self, cr, uid, ids, field_name, arg, context=None):
        """Compute freight percentage
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            uom = 1.0
            if line.product_uom_id.uom_type =='reference':
                uom = 1.0
            else:
                if line.product_uom_id.uom_type =='bigger':
                    uom = line.product_uom_id.factor_inv
                else:
                    uom = line.product_uom_id.factor
            if line.order_id.total_weight:
                res[line.id] = ((line.product_id.weight * uom * line.quantity) / line.order_id.total_weight) * 100
            else:
                res[line.id] = 0.0
        return res

    def _compute_freight_assigned(self, cr, uid, ids, field_name, arg, context=None):
        """Compute freight assigned
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.order_id.freight_total * line.freight_percentage) / 100
        return res

    def _compute_product_tariff(self, cr, uid, ids, field_name, arg, context=None):
        """Compute the product tariff
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.product_id.tariff_total
        return res

    _rec_name = 'code'

    _columns = {
        'code': fields.char('Code',size=128),
        'quantity': fields.float('Quantity',digits_compute= dp.get_precision('Product UoM')),
        'unit_price': fields.float('Unit Price',digits_compute= dp.get_precision('Purchase Price')),
        'subtotal': fields.float('Subtotal',digits_compute= dp.get_precision('Purchase Price')),
        'fob_cost': fields.float('FoB Cost',digits_compute= dp.get_precision('Purchase Price')),
        'product_id':fields.many2one('product.product', 'Product'),
        'product_uom_id':fields.many2one('product.uom', 'Units'),
        'order_id':fields.many2one('purchase.import.import.order', 'Import Order'),
        'import_taxes': fields.function(_compute_import_taxes, type='float', digits_compute= dp.get_precision('Purchase Price'), string='Import Taxes'),
        'tax_percentage': fields.function(_compute_tax_percentage, type='float', digits_compute= dp.get_precision('Purchase Price'), string='Tax (%)'),
        'tax_assigned': fields.function(_compute_tax_assigned, type='float',digits_compute= dp.get_precision('Purchase Price'), string='Assigned Taxes'),
        'freight_percentage': fields.function(_compute_freight_percentage, type='float',digits_compute= dp.get_precision('Purchase Price'), string='Freight (%)'),
        'freight_assigned': fields.function(_compute_freight_assigned, type='float',digits_compute= dp.get_precision('Purchase Price'), string='Assigned Freight'),
        'tariff': fields.function(_compute_product_tariff, type='float',digits_compute= dp.get_precision('Purchase Price'), string='Tariff (%)'),
    }

class ImportOrder(osv.Model):
    """ Import Orders """

    _name = 'purchase.import.import.order'

    _inherit = ['mail.thread']

    _description = __doc__

    _track = {
        'state': {
            'purchase_import.mt_order_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'purchase_import.mt_order_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirmed',
            'purchase_import.mt_order_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'purchase_import.mt_order_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        }
    }

    def _compute_total_weight(self, cr, uid, ids, field_name, arg, context=None):
        """Compute total weight
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            total_weight = 0.0
            line_qty = 0
            uom = 1.0
            for line in order.line_ids:
                # Get the product unit of measure
                if line.product_uom_id.uom_type =='reference':
                    uom = 1.0
                else:
                    if line.product_uom_id.uom_type =='bigger':
                        uom = line.product_uom_id.factor_inv
                    else:
                        if line.product_uom_id.factor:
                            uom = line.product_uom_id.factor
                line_qty = line.quantity * uom
                if line.product_id:
                    product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
                    total_weight = total_weight + (line_qty * product.weight)
                else:
                    total_weight = 0.0
            res[order.id] = total_weight
        return res

    def _compute_tax_sum(self, cr, uid, ids, field_name, arg, context=None):
        """Compute total tax sum
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        total_tax_value = 0.0
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.line_ids:
                if line.product_id:
                    product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
                    if not product.tariff_id:
                        raise osv.except_osv(_('Error'),
                            _('The product %s does not have an Import Tariff') % (product.name))
                    total_tax_value = total_tax_value + line.import_taxes
                else:
                    total_tax_value = total_tax_value + 0.0
            res[order.id] = total_tax_value
        return res

    def _compute_purchase_total(self, cr, uid, ids, field_name, arg, context=None):
        """Compute purchase total
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        total = 0.0
        for imports in self.browse(cr, uid, ids, context=context):
            # Get the currency from company
            currency = imports.company_id.currency_id
            for order in imports.imports_order_ids:
                # Get base the exchange rate
                if order.currency_id.id != currency.id:
                    currency_obj = self.pool.get('res.currency')
                    import_currency_rate = currency_obj.get_exchange_rate(cr, uid, order.currency_id,
                        currency, order.date_invoice, context=context)
                else:
                    import_currency_rate = 1
                total = total + (order.amount_untaxed * import_currency_rate)
            res[imports.id] = total
        return res

    def _compute_tax_total(self, cr, uid, ids, field_name, arg, context=None):
        """Compute tax total
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        currency = 1
        total_tax = 0.0
        for order in self.browse(cr, uid, ids, context=context):
            # Get the currency from company
            currency = order.company_id.currency_id
            if order.tax_order_id:
                if order.tax_order_id.currency_id.id != currency.id:
                    currency_obj = self.pool.get('res.currency')
                    import_currency_rate = currency_obj.get_exchange_rate(cr, uid, order.tax_order_id.currency_id,
                        currency, order.tax_order_id.date_invoice, context=context)
                else:
                    import_currency_rate = 1
                for line in order.tax_ids:
                    total_tax = total_tax + line.price_subtotal * import_currency_rate
            else:
                total_tax = 0.0
            res[order.id]= total_tax
        return res

    def _compute_freight_total(self, cr, uid, ids, field_name, arg, context=None):
        """Compute freight total
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            # Get the currency from company
            currency = order.company_id.currency_id
            if order.freight_order_id:
                # Get base the exchange rate
                if order.freight_order_id.currency_id.id != currency.id:
                    currency_obj = self.pool.get('res.currency')
                    import_currency_rate = currency_obj.get_exchange_rate(cr, uid, order.freight_order_id.currency_id,
                        currency, order.freight_order_id.date_invoice, context=context)
                else:
                    import_currency_rate = 1
                res[order.id] = (order.freight_order_id.amount_untaxed) * import_currency_rate
            else:
                res[order.id] = 0.0
        return res

    def _compute_paid_total(self, cr, uid, ids, field_name, arg, context=None):
        """Compute paid total
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param field_name: The name of the field to be calculated
        @param arg: A standard dictionary
        @param context: A standard dictionary
        @return: A dictionary with the form id: value
        """
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = order.tax_total+ order.freight_total
        return res

    def onchange_freight_order(self, cr, uid, ids, freight_order_id, context=None):
        vals = {}
        if freight_order_id:
            print "wasdasd"
            invoice_obj = self.pool.get('account.invoice')
            invoice = invoice_obj.browse(cr, uid, freight_order_id, context=context)
            vals['freight_currency_id'] = invoice.currency_id.id
        else:
            vals['freight_currency_id'] = False
        return {'value': vals}

    def onchange_tax_order(self, cr, uid, ids, tax_order_id, context=None):
        vals = {}
        if tax_order_id:
            invoice_obj = self.pool.get('account.invoice')
            invoice = invoice_obj.browse(cr, uid, tax_order_id, context=context)
            vals['tax_currency_id'] = invoice.currency_id.id
        else:
            vals['tax_currency_id'] = False
        return {'value': vals}

    def action_confirm(self, cr, uid, ids, context=None):
        name = self.pool.get('ir.sequence').get(cr, uid, 'purchase.import.impord')
        self.write(cr, uid, ids, {'state': 'confirmed','name': name}, context=context)
        return True

    def action_set_average_price(self, cr, uid, ids, context=None):
        res = {}
        for imports in self.browse(cr, uid, ids, context=context):
            total_weight = 0
            order_tax = 0
            product_freight = 0
            product_tax = 0
            for line in imports.line_ids:
                if line.quantity == 0 or line.product_id.weight == 0.0:
                    raise osv.except_osv(_('Error'),
                        _('The order could not be processed. The product %s has a '
                          'weight of 0 or the product quantity equals to 0') % (line.product_id.name))
                #Update price per weight
                if imports.freight_order_id:
                    product_freight = line.freight_assigned
                #Update price per taxes
                if imports.tax_order_id:
                    product_tax= line.tax_assigned
                add_cost = (product_tax + product_freight) / line.product_id.qty_available
                cost = add_cost  + line.product_id.standard_price
                
                self.pool.get('purchase.import.product.import.history').create(cr, uid, {
                    'name': self.pool.get('ir.sequence').get(cr, uid, 'purchase.import.proimphis'),
                    'import_number': imports.name,
                    'product_id': line.product_id.id,
                    'last_price': line.product_id.standard_price,
                    'tax_percentage': line.tax_percentage,
                    'tax_total': line.tax_assigned / line.quantity,
                    'freight_percentage':  line.freight_percentage,
                    'freight_total': line.freight_assigned / line.quantity,
                    'import_total': add_cost,
                    }, context=context)
                if line.product_id.cost_method == 'average':
                    line.product_id.write({
                        'standard_price': cost
                        }, context=context)
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def create(self, cr, uid, values, context=None):
        res = []
        tax_ids = []
        inv_obj = self.pool.get('account.invoice')
        invoices = values['imports_order_ids']
        taxes = values['tax_order_id']
        if taxes:
            for inv in inv_obj.browse(cr, uid, [taxes] , context=context):
                for line in inv.invoice_line:
                    tax_ids.append(line.id)
        values['tax_ids'] = [[6,False,tax_ids]]
        res= super(ImportOrder, self).create(cr, uid, values, context=context)
        # Get the currency from company
        company_obj = self.pool.get('res.company')
        currency = company_obj.browse(cr, uid, values['company_id'], context=context).currency_id
        for inv in inv_obj.browse(cr, uid, invoices[0][2]):
            # Get base the exchange rate
            if inv.currency_id.id != currency.id:
                currency_obj = self.pool.get('res.currency')
                import_currency_rate = currency_obj.get_exchange_rate(cr, uid, inv.currency_id,
                    currency, inv.date_invoice, context=context)
            else:
                import_currency_rate = 1
            for line in inv.invoice_line:
                self.pool.get('purchase.import.import.order.line').create(cr, uid, {
                    'code': self.pool.get('ir.sequence').get(cr, uid, 'purchase.import.impordlin'),
                    'quantity': line.quantity,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.uos_id.id,
                    'fob_cost': line.price_unit,
                    'unit_price': line.price_unit * import_currency_rate,
                    'subtotal': line.price_subtotal * import_currency_rate,
                    'order_id': res,
                    }, context=context)
        return res

    def write(self, cr, uid, ids, values, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            tax_ids = []
            import_currency_rate = 1
            inv_obj = self.pool.get('account.invoice')
            line_obj = self.pool.get('purchase.import.import.order.line')
            if 'tax_order_id' in values:
                taxes = values['tax_order_id']
                if taxes:
                    for inv in inv_obj.browse(cr, uid, [taxes], context=context):
                        for line in inv.invoice_line:
                            tax_ids.append(line.id)
                    values['tax_ids'] = [[6,False,tax_ids]]
                else:
                    values['tax_id'] = [[6,False,[]]]
            super(ImportOrder, self).write(cr, uid, ids, values, context=context)
            for line in order.line_ids:
                line_obj.unlink(cr, uid, line.id)
            order = self.browse(cr, uid, order.id, context=context)
            # Get the company currency
            currency = order.company_id.currency_id
            for inv in order.imports_order_ids:
                # Get base the exchange rate
                if inv.currency_id.id != currency.id:
                    currency_obj = self.pool.get('res.currency')
                    import_currency_rate = currency_obj.get_exchange_rate(cr, uid, inv.currency_id,
                        currency, inv.date_invoice, context=context)
                else:
                    import_currency_rate = 1
                for line in inv.invoice_line:
                    self.pool.get('purchase.import.import.order.line').create(cr, uid, {
                        'code': self.pool.get('ir.sequence').get(cr, uid, 'purchase.import.impordlin'),
                        'quantity': line.quantity,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.uos_id.id,
                        'fob_cost': line.price_unit,
                        'unit_price': line.price_unit * import_currency_rate,
                        'subtotal': line.price_subtotal * import_currency_rate,
                        'order_id': order.id,
                        }, context=context)
        return True

    _order = 'date desc'

    _columns = {
        'name': fields.char('Order Number', size=128, readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True,),
        'voucher_ids': fields.one2many('purchase.import.import.voucher', 'order_id', 'Vouchers'),
        'origin_id' : fields.many2one('res.country', 'Origin', required=True),
        'freight_order_id':fields.many2one('account.invoice', 'Freight Invoice'),
        'tax_order_id':fields.many2one('account.invoice', 'Taxes Invoice'),
        'date_arrive' : fields.date('Arrive Date'),
        'date_due' : fields.date('Date Limit'),
        'total_weight': fields.function(_compute_total_weight, type='float', string='Total Weight (Kg)'),
        'sum_tax_value': fields.function(_compute_tax_sum, type='float', string='Product Registered Taxes'),
        'purchase_total': fields.function(_compute_purchase_total, type='float', string='Purchase Total'),
        'tax_total': fields.function(_compute_tax_total, type='float', string='Total Taxes'),
        'freight_total': fields.function(_compute_freight_total, type='float', string='Total Freight'),
        'paid_total': fields.function(_compute_paid_total, type='float', string='Import Total'),
        'line_ids': fields.one2many('purchase.import.import.order.line', 'order_id', string='Products', readonly=True),
        'tax_ids': fields.many2many('account.invoice.line', 'import_tax_id', 'imports_id', 'line_id', string='Taxes Invoice'),
        'imports_order_ids': fields.many2many('account.invoice', 'import_invoice_id', 'imports_id', 'invoice_id', string='Products Invoice'),
        'freight_ids': fields.related('freight_order_id', 'invoice_line', type='one2many', relation='account.invoice.line', string='Freight'),
        'freight_currency_id': fields.related('freight_order_id', 'currency_id', type='many2one', relation='res.currency', string='Freight Currency', readonly=True),
        'tax_currency_id': fields.related('tax_order_id', 'currency_id', type='many2one', relation='res.currency', string='Tax Currency', readonly=True),
        'notes': fields.text('Notes'),
        'date' : fields.datetime('Create Date', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Processed'), ('cancel', 'Cancelled')], string='State')
    }

    _defaults = {
        'state': 'draft',
        'company_id': lambda slf,cr,uid,ctx: slf.pool.get('res.company')._company_default_get(cr, uid, 'purchase.import.order', context=ctx),
        'date': lambda *a: datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S'),
    }

class Voucher(osv.Model):
    """Import Vouchers"""

    _name = 'purchase.import.import.voucher'

    _description = __doc__

    def _compute_cif_real(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.order_id:
                res[voucher.id] = voucher.order_id.purchase_total +  voucher.order_id.freight_total
            else:
                res[voucher.id] = 0.0
        return res

    def _compute_cif_dolars(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.currency_rate  != 0.0:
                res[voucher.id] = voucher.cif_real / voucher.currency_rate
            else:
                res[voucher.id] = 0.0
        return res

    _rec_name = 'number'

    _order = 'date desc'

    _columns = {
        'number': fields.char('Voucher Number', size=128, required=True),
        'date' : fields.date('Date'),
        'bidder_id' : fields.many2one('res.partner', string='Bidder'),
        'agent_number': fields.char('Agent Number', size=64),
        'regime': fields.char('Regime', size=64),
        'type': fields.selection([('import','Import'),('export','Export')], string='Type'),
        'mode': fields.char('Mode', size=64),
        'type_audit': fields.char('Audit Type', size=64),
        'number_packages': fields.float('Number of Packages'),
        'weight': fields.float('Weight'),
        'net_weight': fields.float('Net Weight'),
        'cif_real': fields.function(_compute_cif_real, type='float', string='CIF Real', help='Cost, insurance and freight'),
        'cif_paid': fields.float('CIF Paid', required=True),
        'cif_dolars': fields.function(_compute_cif_dolars,  type='float', string='CIF Dolars', help='Cost, insurance and freight'),
        'currency_rate': fields.float('Currency Rate', required=True),
        'order_id': fields.many2one('purchase.import.import.order', string='Import Order', ondelete='set null', select=True),
    }

    _defaults = {
        'date': lambda slf, cr, uid, ctx: date.strftime(date.today(), "%Y-%m-%d"),
        'type': 'import',
        }