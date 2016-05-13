# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm, osv
import openerp.addons.decimal_precision as dp

class accountDistributionline(orm.Model):
    _name = "account.distribution.line"
    _description = "Account Distribution Line"
    
    """
        This class is a base for cash flow distribution (Cash Flow Report) and
        account move line distribution (Budget). In this class exists functions
        that they have in common and their are used for both models.
  
        Also, in this model exists all fields that budget and cash flow report
        have in common. Then, each model create a new model that inherit from 
        this model and add their own fields.
    """
    _columns = {         
         'account_move_line_id': fields.many2one('account.move.line', 'Account Move Line', ondelete="cascade"),
         'distribution_percentage': fields.float('Distribution Percentage', required=True, digits_compute=dp.get_precision('Account'),),
         'distribution_amount': fields.float('Distribution Amount', digits_compute=dp.get_precision('Account'), required=True),
         'target_account_move_line_id': fields.many2one('account.move.line', 'Target Move Line'),         
    }  
 