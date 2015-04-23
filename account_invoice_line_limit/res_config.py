# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.osv import osv,fields
from openerp.tools.translate import _

class ResCompany(osv.Model):
    _inherit = 'res.company'
    _columns = {
            'maximum_invoice_lines': fields.integer('Maximum quantity of invoice lines per Invoice',
            help='This allows define the maximum quantity of invoices lines per Invoice. If use value 0, the quantity is not limited '),
            'maximum_description_product': fields.integer('Maximum quantity of character in description of product',
            help='This allows define the maximum quantity of character in description of product. If use value 0, the quantity is not limited '),
            }
class purchase_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    def get_default_maximum_description_product(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'maximum_description_product': user.company_id.maximum_description_product
        }
    def set_maximum_description_product(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write({
            'maximum_description_product': config.maximum_description_product
            })
    def get_default_maximum_invoice_lines(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'maximum_invoice_lines': user.company_id.maximum_invoice_lines
        }
    def set_maximum_invoice_lines(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write({
            'maximum_invoice_lines': config.maximum_invoice_lines
            })
        
    _columns = {
            'maximum_invoice_lines': fields.integer('Maximum quantity of invoice lines per Invoice',
            help='This allows define the maximum quantity of invoices lines per Invoice. If use value 0, the quantity is not limited '),
            'maximum_description_product': fields.integer('Maximum quantity of character in description of product',
            help='This allows define the maximum quantity of character in description of product. If use value 0, the quantity is not limited '),
            }
    _defaults={
               'maximum_invoice_lines':0,
               'maximum_description_product':0,
               }