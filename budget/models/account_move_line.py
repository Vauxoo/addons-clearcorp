# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # ========================================================================
    #
    # distribution_percentage_sum compute the percentage for the
    # account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    #
    # distribution_amount_sum compute the amount for the account.move.line.
    # Check the account.move.line.distribution and sum where id is the same for
    # account.move.line.
    #
    # account_move_lines_mod method return the account.move.line id's where the
    # store apply the change. This method is necessary to create a store. This
    # help to compute in a "automatic way" those fields (percentage and sum)
    # and is easier to get this values from those fields.
    #
    # =========================================================================

    @api.multi
    def _sum_distribution_per(self):
        res = {}
        for line in self:
            res[line.id] = 0.0
        query = """SELECT amld.id, SUM(amld.distribution_percentage) AS dis_per FROM
        'account_move_line_distribution amld
        'WHERE amld.id IN %s GROUP BY amld.id"""
        params = self._ids
        self._cr.execute(query, params)
        for row in self._cr.dictfetchall():
            res[row['id']] = row['dis_per']
        return res

    @api.multi
    def _sum_distribution_amount(self):
        res = {}
        for line in self:
            res[line.id] = 0.0
        query = """SELECT amld.id, SUM(amld.distribution_amount) AS dis_amount FROM
        'account_move_line_distribution amld
        'WHERE amld.id =  %s GROUP BY amld.id""" % id
        self._cr.execute(query)
        for row in self._cr.dictfetchall():
            res[row['id']] = abs(row['dis_amount'])
        return res

    @api.multi
    def _account_move_lines_mod(self, amld_ids):
        list_amld = []
        amld_obj = self.env['account.move.line.distribution']
        for line in amld_obj.browse(amld_ids):
            list_amld.append(line.account_move_line_id.id)
        return list_amld

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
