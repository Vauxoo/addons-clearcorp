from osv import osv
from osv import fields
import os
import tools
from tools.translate import _
from tools.safe_eval import safe_eval as eval

class res_company(osv.osv):
      _inherit = 'res.company'
      _columns =  {
        'sale_order_footer': fields.text('Sale Order Footer'),
        'show_sale_order_footer': fields.boolean('Show Sale Order Footer'),       
            } 
      _defaults = {
        'show_sale_order_footer': False        
            }
      

class sale_order(osv.osv):
      _inherit = 'sale.order'
      _columns =  {
        'expiration_date': fields.date('Expiration date'),       
            } 
