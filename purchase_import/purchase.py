import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import osv, fields
import netsvc
import pooler
from tools.translate import _
import decimal_precision as dp
from osv.orm import browse_record, browse_null
import logging


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'numero_parte': fields.related('product_id','numero_parte',string='Numero Parte',readonly=True,type="char")
    }
purchase_order_line()
