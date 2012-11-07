#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

class ResCompany(orm.Model):
    _inherit =  "res.company"
    
    _columns = {
        'property_asset_view_account':      fields.many2one('account.account','Asset view account'),
        'property_liability_view_account':  fields.many2one('account.account','Liability view account'),
        'property_equity_view_account':     fields.many2one('account.account','Equity view account'),
        'property_income_view_account':     fields.many2one('account.account','Income view account'),
        'property_expense_view_account':    fields.many2one('account.account','Expense view account'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
