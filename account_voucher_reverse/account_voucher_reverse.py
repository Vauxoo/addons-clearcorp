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

class AccountVoucherReverse(osv.osv):
    _name = 'account.voucher'
    _inherit = 'account.voucher'

    _columns = {
        'move_line_reverse_ids' : fields.related('move_id', 'move_reverse_id', 'line_id', type='one2many', relation='account.move.line', string='Journal Items Reverse', readonly=True),
        'state':fields.selection(
            [('draft','Draft'),
             ('proforma','Pro-forma'),
             ('posted','Posted'),
             ('reverse','Reverse'),
             ('cancel','Cancelled')
            ], 'State', readonly=True, size=32,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma state,voucher does not have an voucher number. \
                        \n* The \'Posted\' state is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Reverse\' state is used when user reverse voucher \
                        \n* The \'Cancelled\' state is used when user cancel voucher.'),
    }

    def reverse_voucher(self, cr, uid, ids, context=None):
        for voucher_id in ids:
            voucher = self.pool.get('account.voucher').browse(cr, 1, voucher_id, context=context)
            if voucher.move_id:
                self.pool.get('account.move').reverse(cr, uid, [voucher.move_id.id], context=context)
            self.write(cr, uid, [voucher_id], {'state' : 'reverse'}, context=context)
        return {}













