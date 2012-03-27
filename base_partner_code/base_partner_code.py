
from osv import osv,fields

class res_partner(osv.osv):





    _description='Partner'
    _name = "res.partner"
    _inherit = "res.partner"
    _order = "name"
    _columns = {
            'code': fields.char('Internal Code', size=16, select=1),
    }
res_partner()
