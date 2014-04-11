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

from osv import osv, fields
from tools.translate import _

class GenerateExchangeRatesWizard(osv.osv_memory):
    _name = "generate.exchange.rates.wizard"
    _description = "generate.exchange.rates.wizard"
    
    _columns = {
        'reference': fields.char('Reference', size=256, required=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, help="Choose the journal for the move automatically generated"),
        'period_id': fields.many2one('account.period', 'Period', required=True, help="Choose the journal for the move automatically generated"),
        'exchange_rate_date': fields.date('Force adjustment date', help="The moves are adjusted before this date and the exchange rate used will be on this date"),
    }
   
    def _get_period(self, cr, uid, context=None):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        return False
 
    _defaults = {
        'period_id': _get_period,
    }

    def generate_exchange_rates(self, cr, uid, ids, context):
        account_move_obj = self.pool.get('account.move')
        data = self.browse(cr, uid, ids, context=context)
        reference = data[0].reference
        journal = data[0].journal_id
        period = data[0].period_id
        exchange_rate_date = data[0].exchange_rate_date or False
        created_move_id = account_move_obj.generate_adjustment_move(cr, uid, reference, journal, period, exchange_rate_date, context=context)
        return {
            'name': _('Created Account Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': "[('id','=',"+str(created_move_id)+")]",
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
