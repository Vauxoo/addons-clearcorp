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


from openerp import models, api


class Order(models.Model):

    _inherit = 'pos.order'

    @api.multi
    def _create_account_move_line(self, session=None, move_id=None):
        res = super(Order, self)._create_account_move_line(
            session=session, move_id=move_id)

        property_obj = self.env['ir.property']

        for order in self:

            current_company = order.sale_journal.company_id
            account_def = property_obj.get(
                'property_account_receivable', 'res.partner')

            order_account = order.partner_id and \
            order.partner_id.property_account_receivable and \
            order.partner_id.property_account_receivable.id or \
            account_def and account_def.id or current_company.account_receivable.id
            
            if order.account_move:
                account = order.session_id.config_id.account_id
                if account:
                    self._cr.execute("""UPDATE account_move_line SET account_id = %s
                        WHERE move_id = %s AND account_id = %s;""",
                        (account.id, order.account_move.id, order_account,))
        return res

    def add_payment(self, cr, uid, order_id, data, context=None):
        statement_id = super(Order, self).add_payment(
            cr, uid, order_id, data, context=context)

        statement_line_obj = self.pool.get('account.bank.statement.line')
        statement_obj = self.pool.get('account.bank.statement')

        if statement_id:
            order = self.browse(cr, uid, order_id, context=context)
            account = order.session_id.config_id.account_id
            if account:
                for line in order.statement_ids:
                    if line.statement_id.id == statement_id:
                        statement_line_obj.write(cr, uid, line.id,
                            {'account_id': account.id}, context=context)
                statement_obj.write(cr, uid, statement_id,
                    {'account_id': account.id}, context=context)

        return statement_id

