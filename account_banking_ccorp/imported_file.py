# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 EduSense BV (<http://www.edusense.nl>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

##############################################################################
#    Collaboration by:
#    CLEARCORP S.A.- Copyright (C) 2009-TODAY 
#    (<http://clearcorp.co.cr>).
###############################################################################

from openerp.osv import osv, fields
import time

class account_banking_imported_file(osv.Model):
    '''Imported Bank Statements File'''
    _name = 'account.banking.ccorp.imported.file'
    
    _description = __doc__
    
    _rec_name = 'date'
    
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', select=True, readonly=True),
        'date': fields.datetime('Import Date', readonly=True, select=True),
        'format': fields.char('File Format', size=20, readonly=True),
        'file': fields.binary('Raw Data', readonly=True),
        'user_id': fields.many2one('res.users', 'Responsible User', readonly=True, select=True),
        'state': fields.selection([('unfinished', 'Unfinished'),
                                   ('error', 'Error'),
                                   ('review', 'Review'),
                                   ('ready', 'Finished'),],
                                  'State', select=True, readonly=True),
        'statement_ids': fields.one2many('account.bank.statement', 'banking_id',
                                         'Statements',readonly=False,),
        'bank_id': fields.many2one('res.partner.bank', 'Bank', readonly=True),
    }
    
    _defaults = {
                 'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                 'user_id': lambda self, cursor, uid, context: uid,
                 }