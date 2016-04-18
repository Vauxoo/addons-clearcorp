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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class AccountMoveLine(osv.Model):
    _inherit = 'account.move.line'
    
    #===========================================================================
    # 
    # distribution_percentage_sum compute the percentage for the account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    # 
    # distribution_amount_sum compute the amount for the account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    # 
    #_account_move_lines_mod method return the account.move.line id's where the
    # store apply the change. This method is necessary to create a store. This
    # help to compute in a "automatic way" those fields (percentage and sum) and
    # is more easy to get this values from those fields. 
    #
    #===========================================================================
    
    def _sum_distribution_per(self, cr, uid, ids, field_name, args, context=None):
        res = {}       
        for id in ids:
            res[id] =0.0
        query = 'SELECT amld.id, SUM(amld.distribution_percentage) AS dis_per FROM '\
        'account_move_line_distribution amld '\
        'WHERE amld.id IN %s GROUP BY amld.id'
        params = (tuple(ids),)
        cr.execute(query,params)
        for row in cr.dictfetchall():
            res[row['id']] = row['dis_per']        
        return res
    
    def _sum_distribution_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for id in ids:
            res[id] =0.0      
        query = 'SELECT amld.id, SUM(amld.distribution_amount) AS dis_amount FROM '\
        'account_move_line_distribution amld '\
        'WHERE amld.id =  %s GROUP BY amld.id' % id
        cr.execute(query)
        for row in cr.dictfetchall():
            res[row['id']] = abs(row['dis_amount'])        
        return res
           
    def _account_move_lines_mod(self, cr, uid, amld_ids, context=None):
        list = []
        amld_obj = self.pool.get('account.move.line.distribution')
        
        for line in amld_obj.browse(cr, uid, amld_ids, context=context):
            list.append(line.account_move_line_id.id)
        return list
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        for line in self.browse(cr, uid, ids, context=context):
            new_line = ""
            deb=""
            cred = ""
            am_curr = ""
            
            if line.debit:
                deb= _( "D:") + str(round(line.debit, self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')))
            if line.credit:
                cred= _( "C:") + str(round(line.credit, self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')))
            if line.amount_currency:
                am_curr= _( "AC:") + str(round(line.amount_currency, self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')))
                
            if line.ref:
                result.append((line.id, (line.move_id.name or '')+' ('+line.ref+')'+" "+ deb +" "+ cred +" "+ am_curr))
            else:
                result.append((line.id, line.move_id.name +" "+ deb +" "+ cred +" "+ am_curr))
        return result
    
    def copy(self, cr, uid, id, default, context=None):
       default = {} if default is None else default.copy()
       default.update({
            'budget_move_lines':False
        })
       return super(AccountMoveLine, self).copy(cr, uid, id, default, context)
        
        
    def copy_data(self, cr, uid, id, default=None, context=None):
        default = {} if default is None else default.copy()
        default.update({
            'budget_move_lines':False
            })
        return super(AccountMoveLine, self).copy_data(cr, uid, id, default, context)
    
    _columns = {
        #=======Budget Move Line
        'budget_move_lines': fields.one2many('budget.move.line','move_line_id', 'Budget Move Lines'),
        
        #=======Percentage y amount distribution
        'distribution_percentage_sum': fields.function(_sum_distribution_per, type="float", method=True, string="Distributed percentage",
                                                   store={'account.move.line.distribution': (_account_move_lines_mod, ['distribution_amount','distribution_percentage'], 10)}),        
        'distribution_amount_sum': fields.function(_sum_distribution_amount, type="float", method=True, string="Distributed amount",
                                                   store={'account.move.line.distribution': (_account_move_lines_mod, ['distribution_amount','distribution_percentage'], 10)}),        
        
        #=======account move line distributions
        'account_move_line_dist': fields.one2many('account.move.line.distribution','account_move_line_id', 'Account Move Line Distributions'),
        'type_distribution':fields.related('account_move_line_dist','type', type="selection", relation="account.move.line.distribution", string="Distribution type", selection=[('manual', 'Manual'), ('auto', 'Automatic')]),
        
        #======budget program line
        'budget_program_line': fields.many2one('budget.program.line', 'Budget Program Line'),
    }
    
    _defaults = {
        'distribution_percentage_sum': 0.0, 
        'distribution_amount_sum': 0.0,
    }
