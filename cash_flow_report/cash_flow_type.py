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

from osv import fields,orm
import decimal_precision as dp
from openerp.tools.translate import _

class cashFlowtype(orm.Model):
    
    _name = "cash.flow.type"
    _description = "Cash Flow Type"
    
    _columns = {
        'name': fields.char('Name', size=128), 
        'code': fields.char('Code', size=128),
        'type': fields.selection(
                    [('operation','Operation'),
                     ('investment','Investment'),
                     ('financing','Financing')],
                     'Type',), 
    }     
    
class accountCashflowType(orm.Model):         
    
    _inherit = "account.account"
    _columns = {
        'cash_flow_type': fields.many2one('cash.flow.type', 'Cash Flow Type')                
    }
    
class accountCashflowTypedsitribution(orm.Model):
    _name = "account.cash.flow.distribution"
    _description = "Account Cash Flow Distribution"
    
    _columns = {
        'account_move_line_id': fields.many2one('account.move.line', 'Account Move Line', required=True),
        'distribution_amount': fields.float('Distribution Amount', required=True, digits_compute=dp.get_precision('Account'),),
        'target_account_move_line': fields.many2one('account.move.line', 'Target Account Move Line', required=True),
        'reconcile_ids': fields.many2many('account.move.reconcile','cash_flow_reconcile_distribution_ids', string='Reconciles'),
    }

    _defaults = {
        'distribution_amount': 0.0,
    }
    
