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

from openerp.osv import fields, orm

class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'
    
    #===========================================================================
    # 
    # distribution_percentage_sum_cash compute the percentage for the account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    # 
    # distribution_amount_sum_cash compute the amount for the account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    # 
    #_account_move_lines_mod method return the account.move.line id's where the
    # store apply the change. This method is necessary to create a store. This
    # help to compute in a "automatic way" those fields (percentage and sum) and
    # is more easy to get this values from those fields. 
    #
    #===========================================================================
    
    def _sum_distribution_per_cash(self, cr, uid, ids, field_name, args, context=None):
        res = {}       
        for id in ids:
            res[id] =0.0
        query = 'SELECT cfd.id, SUM(cfd.distribution_percentage) AS dis_per FROM '\
        'cash_flow_distribution cfd '\
        'WHERE cfd.id IN %s GROUP BY cfd.id'
        params = (tuple(ids),)
        cr.execute(query,params)
        for row in cr.dictfetchall():
            res[row['id']] = row['dis_per']        
        return res
    
    def _sum_distribution_amount_cash(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for id in ids:
            res[id] =0.0      
        query = 'SELECT cfd.id, SUM(cfd.distribution_amount) AS dis_amount FROM '\
        'cash_flow_distribution cfd '\
        'WHERE cfd.id =  %s GROUP BY cfd.id' % id
        cr.execute(query)
        for row in cr.dictfetchall():
            res[row['id']] = abs(row['dis_amount'])        
        return res
           
    def _account_move_lines_mod_cash(self, cr, uid, cfd_ids, context=None):
        list = []
        cfd_obj = self.pool.get('cash.flow.distribution')
        
        for line in cfd_obj.browse(cr, uid, cfd_ids, context=context):
            list.append(line.account_move_line_id.id)
        return list
        
    _columns = {
      
        #=======Percentage y amount distribution
        'distribution_percentage_sum_cash': fields.function(_sum_distribution_per_cash, type="float", method=True, string="Distributed Cash Flow percentage",
                                                   store={'cash.flow.distribution': (_account_move_lines_mod_cash, ['distribution_amount','distribution_percentage'], 10)}),        
        'distribution_amount_sum_cash': fields.function(_sum_distribution_amount_cash, type="float", method=True, string="Distributed Cash Flow amount",
                                                   store={'cash.flow.distribution': (_account_move_lines_mod_cash, ['distribution_amount','distribution_percentage'], 10)}),        
        
        #=======cash flow line distributions
        'cash_flow_line_dist': fields.one2many('cash.flow.distribution','account_move_line_id', 'Cash Flow Distributions'),
    }
    
    _defaults = {
        'distribution_percentage_sum_cash': 0.0, 
        'distribution_amount_sum_cash': 0.0,
    }