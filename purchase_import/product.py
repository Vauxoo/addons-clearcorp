from osv import osv, fields
import decimal_precision as dp
import math
import logging
import re
from tools.translate import _

class product_product(osv.osv):
    _inherit = "product.product"
    def _calc_amount_tax(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        total_tax = 0
        for product in self.browse(cr, uid, ids):
            for tax in product.import_taxes:
                total_tax = total_tax + tax.value
            res[product.id] = total_tax
        return res

    _columns = {
        'tariff_id' : fields.many2one('purchase.import.tariff', 'Arancel'),
        'tax_total': fields.function(_calc_amount_tax, method=True, string='Impuestos', type='float',help='Taxes from import'),
        'import_taxes': fields.related('tariff_id','tax_id',type='one2many',relation='purchase.import.tax',string='Detalle'),
    }
product_product()
