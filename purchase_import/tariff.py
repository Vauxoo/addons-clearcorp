from osv import osv, fields
import decimal_precision as dp

import math
import logging
import re
from tools.translate import _

class purchase_import_tariff_category(osv.osv):
    _name = 'purchase.import.tariff.category'
    _columns = {
        'code': fields.char('Code',size=64),
        'name': fields.char('Name',size=64),
        'description': fields.char('Description',size=64),
    }
purchase_import_tariff_category()


class purchase_import_tariff(osv.osv):
    _name = 'purchase.import.tariff'

    def _calc_amount_tax(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        total_tax = 0
        for tariff in self.browse(cr, uid, ids):
            for tax in tariff.tax_id:
                total_tax = total_tax + tax.value
            res[tariff.id] = total_tax
        return res

    _columns = {
        'name': fields.char('Code',size=64),
        'description': fields.char('Description',size=64),
        'category' : fields.many2one('purchase.import.tariff.category', 'Category'),
        'tax_id': fields.one2many('purchase.import.tax', 'tariff_id', 'Tax'),

        'tariff_total': fields.function(_calc_amount_tax, method=True, string='Total Tax', type='float',help='Taxes from import'),
    }
purchase_import_tariff()

class purchase_import_tax(osv.osv):
    _name = 'purchase.import.tax'
    _columns = {
        'code': fields.char('Code',size=64, required=True),
        'name': fields.char('Name',size=64, required=True),
        'description': fields.char('Description',size=64),
        'value': fields.float('Value', required=True),
        'tariff_id' : fields.many2one('purchase.import.tariff', 'Tariff'),
    }
purchase_import_tax()
