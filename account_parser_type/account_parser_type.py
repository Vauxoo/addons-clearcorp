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

import netsvc
from osv import fields, orm
import tools
from tools.translate import _
from account_banking.parsers import models

def parser_types(*args, **kwargs):
    '''Delay evaluation of parser types until start of wizard, to allow
       depending modules to initialize and add their parsers to the list
    '''
    return models.parser_type.get_parser_types()

class BankAccounts(orm.Model):
    _inherit =  "res.partner.bank"
    
    _columns = {
        'parser': fields.selection(
            parser_types, 'Parser type',
            states={
                'ready': [('readonly', True)],
                'error': [('readonly', True)],
                }, help="Parser type for import bank extract",
            ),
    }
