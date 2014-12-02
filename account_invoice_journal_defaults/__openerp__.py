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
{
    'name': 'account_invoice_journal_defaults',
    'version': '1.0',
    'category': 'Accounting & Finance',
    "sequence": 4,
    'complexity': "normal",
    'description': '''
                * account_id and journal_id added to onchange_partner
                * account_id added in onchange_journal 
                * account_id associated with the journal or with the account in the partner
                * account_id change to read-only                
                ''',
    "author" : 'CLEARCORP S.A',
    'website':'http://www.clearcorp.co.cr',
    "depends" : ['account'],
    'update_xml': [
        'account_invoice_journal_defaults_view.xml',
        ],
    "auto_install": False,
    "application": False,
    "installable": True,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
