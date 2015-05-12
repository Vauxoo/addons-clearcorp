# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
 