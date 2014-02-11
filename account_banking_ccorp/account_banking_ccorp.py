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
#    along with this program.  If not, see <http://www.gnu.org/licens    es/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

from parsers import models

def parser_types(*args, **kwargs):
    '''Delay evaluation of parser types until start of wizard, to allow
       depending modules to initialize and add their parsers to the list
    '''
    return models.parser_type.get_parser_types()

class resPartnerBank(osv.Model):
    _inherit = "res.partner.bank"
    
    _columns = {
                'parser_types': fields.selection(
                                parser_types,
                                'Parser type',
                                help=_("Parser type used to import bank statements file")),
                'default_credit_account_id': fields.many2one(
                                             'account.account', 'Default credit account',
                                             select=True),
                'default_debit_account_id': fields.many2one('account.account', 'Default debit account',
                                                            select=True),
                }
