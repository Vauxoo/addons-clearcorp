# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Original Module by SIESA (<http://www.siesacr.com>)
#    Refactored by CLEARCORP S.A. (<http://clearcorp.co.cr>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    license, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from openerp.osv import osv, fields

class Product(osv.Model):

    _inherit = 'product.product'

    _columns = {
        'tariff_id' : fields.many2one('purchase.import.tariff', 'Tariff'),
        'tariff_total': fields.related('tariff_id','tariff_total',type='float',string='Total Taxes', readonly=True),
        'tax_ids': fields.related('tariff_id','tax_ids',type='one2many',relation='purchase.import.tax',string='Taxes', readonly=True),
        'import_history_ids': fields.one2many('purchase.import.product.import.history', 'product_id', 'Product Import History'),
    }