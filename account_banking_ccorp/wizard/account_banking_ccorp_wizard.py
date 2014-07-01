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
# Many thanks to our contributors
#
# Kaspars Vilkens (KNdati): lenghty discussions, bugreports and bugfixes
# Stefan Rijnhart (Therp): bugreport and bugfix
# CLEARCORP S.A: Customization and migration to OpenERP 7.0
'''
This module contains the business logic of the wizard account_banking_import.
The parsing is done in the parser modules. Every parser module is required to
use parser.models as a mean of communication with the business logic.
'''
from openerp.osv import osv, fields
import time
import netsvc
import base64
import datetime
from tools import config
from tools.translate import _
from account_banking_ccorp.parsers import models
from account_banking_ccorp.parsers.convert import *
from account_banking_ccorp.struct import struct
from account_banking_ccorp import sepa
from banktools import *

import decimal_precision as dp
import re

bt = models.mem_bank_transaction

# This variable is used to match supplier invoices with an invoice date after
# the real payment date. This can occur with online transactions (web shops).
payment_window = datetime.timedelta(days=10)

def parser_types(*args, **kwargs):
    '''Delay evaluation of parser types until start of wizard, to allow
       depending modules to initialize and add their parsers to the list
    '''
    return models.parser_type.get_parser_types()

class bankImportLine(osv.TransientModel):
    _name = 'account.banking.ccorp.bank.import.line'
    
    _description = 'Bank import lines'
    
    _columns = {
        'name': fields.char('Name', size=64),
        'date': fields.date('Date', readonly=True),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'statement_line_id': fields.many2one('account.bank.statement.line',
                                             'Resulting statement line',
                                             readonly=True),
        'type': fields.selection([('supplier','Supplier'),
                                  ('customer','Customer'),
                                  ('general','General')],
                                 'Type', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'statement_id': fields.many2one('account.bank.statement', 'Statement',
                                        select=True, required=True, ondelete='cascade'),
        'ref': fields.char('Reference', size=32),
        'note': fields.text('Notes'),
        'period_id': fields.many2one('account.period', 'Period'),
        'currency': fields.many2one('res.currency', 'Currency'),
        'banking_import_id': fields.many2one('account.banking.ccorp.bank.import.wizard', 'Bank import',
                                             readonly=True, ondelete='cascade'),
        'reconcile_id': fields.many2one('account.move.reconcile', 'Reconciliaton'),
        'account_id': fields.many2one('account.account', 'Account'),
        'invoice_ids': fields.many2many('account.invoice', 'banking_import_line_invoice_rel',
                                        'line_id', 'invoice_id'),
        'payment_order_id': fields.many2one('payment.order', 'Payment order'),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account'),
        'transaction_type': fields.selection([
                                              # TODO: payment terminal etc...
                                              ('invoice', 'Invoice payment'),
                                              ('payment_order_line', 'Payment from a payment order'),
                                              ('payment_order', 'Aggregate payment order'),
                                              ('storno', 'Canceled debit order'),
                                              ('bank_costs', 'Bank costs'),
                                              ('unknown', 'Unknown'),
                                              ], 'Transaction type'),
        'duplicate': fields.boolean('Duplicate'),
        }

class bankImportWizard(osv.TransientModel):
    _name = 'account.banking.ccorp.bank.import.wizard'

    def import_statements_file(self, cr, uid, ids, context):
        '''
        Import bank statements / bank transactions file.
        This method is a wrapper for the business logic on the transaction.
        The parser modules represent the decoding logic.
        '''
        #Get the wizard record and binary file
        bank_import_wizard = self.browse(cr, uid, ids, context)[0]
        #Get the binary file without encoding
        statements_file = bank_import_wizard.file

        user_obj = self.pool.get('res.users')
        company_obj = self.pool.get('res.company')
        statement_obj = self.pool.get('account.bank.statement')
        statement_file_obj = self.pool.get('account.banking.ccorp.imported.file')
        import_transaction_obj = self.pool.get('account.banking.ccorp.bank.import.transaction')
        period_obj = self.pool.get('account.period')
        # Get the parser to parse the file according to
        #the selected account
        parser_code = bank_import_wizard.parser
        parser = models.create_parser(parser_code)
        if not parser:
            raise osv.except_osv(
                _('ERROR!'),
                _('Unable to import parser %(parser)s. Parser class not found.') %
                {'parser': parser_code}
            )
        # Get the user and company
        #Fix the problem with permission of the user
        user = user_obj.browse(cr, uid, uid, context)
        company = bank_import_wizard.company
        '''
            PASS THE PARAMETERS TO PARSER. IT'S MORE EASY AND CLEAR PASS FROM HERE.
            The object bank_import_wizard have all the fields in the wizard.
            For BAC and BCR parsers it's not needed.
        '''
        #account_number used if the file haven't one.
        #Really needed?
        account_number = self.extract_number(bank_import_wizard.account_bank.acc_number)
        #local_currency extracted from account_bank
        if bank_import_wizard.account_bank.currency_id:
            local_currency = bank_import_wizard.account_bank.currency_id.name
        else:
            local_currency = 'CRC'
        #TODO: Fields used only by the davivienda's parser, must be removed and added
        #in the custom parser's module
        date_from_str = bank_import_wizard.date_from
        date_to_str = bank_import_wizard.date_to
        #TODO: Fields used only by the BNCR's parser, must be removed and added
        #in the custom parser's module
        #In BNCR's parser the file does not have the initial balance, 
        #the extract must have a initial or ending balance.
        #With ending_balance compute the initial_balance
        ending_balance = float(bank_import_wizard.ending_balance)
        '''
            For BCR and BAC parsers. (this parsers don't need account_number, local_currency, 
            date_from_str, date_to_str parameters, because the file have this information. 
            The file for Davivienda don't have that information.
            
            To prevent other parsers not work with this specific parameter passing, ** kwargs is used, which allows dynamically pass parameters 
            to functions. In all parsers must specify this parameter, if required pass parameters, passed through this dictionary, but the method 
            is unknown and there is no need to change the original format parsers.
            
            account_number=account_number, local_currency=local_currency, date_from_str=date_from_str, 
            date_to_str=date_to_str = pass through **kwargs and extract kwargs['parameter_name].
            
            parse is a generic name method that is used by all the parsers. When is selected the parser, call the method that 
            corresponds to parser and execute the other methods. Not recommended change the name for this method, because should create 
            a specific wizard for each parser that is created. '''
        '''
            It changes the way file encoding. Now it's parser was chosen and not the wizard.
            The parser has a field (type_file) which is a list of file types supported by each 
            of the types of parser
            The statements is the file without encondig. Change parameter data for statements_file
            and the parser encoding the file.'''
        #Call the parser's parse method.
        statements = parser.parse(cr, statements_file, account_number = account_number, 
                                  local_currency = local_currency, date_from_str = date_from_str, 
                                  date_to_str = date_to_str,ending_balance = ending_balance,
                                  real_account= bank_import_wizard.account_bank.acc_number)
        if any([x for x in statements if not x.is_valid()]):
            raise osv.except_osv(
                _('ERROR!'),
                _('The imported statements appear to be invalid! Check your file.'))
        # Create the file now, as the statements need to be linked to it
        import_id = statement_file_obj.create(cr, uid, dict(company_id = company.id,
                                                            file = statements_file,
                                                            state = 'unfinished',
                                                            format = parser.name,
                                                            bank_id = bank_import_wizard.account_bank.id))
        #Extract country_code from parser if available
        bank_country_code = False
        if hasattr(parser, 'country_code'):
            bank_country_code = parser.country_code
        # Caching
        info = {}
        imported_statement_ids = []
        transaction_ids = []

        for statement in statements:
            # Create fallback currency code
            currency_code = statement.local_currency or company.currency_id.name
            # Obtain account_info
            # Check cache for account info/currency
            if statement.local_account in info and \
            currency_code in info[statement.local_account]:
                account_info = info[statement.local_account][currency_code]
            else:
                # Pull account info/currency
                account_info = None
                try:
                    account_info = get_company_bank_account(
                    self.pool, cr, uid, statement.local_account,
                    statement.local_currency, company, bank_import_wizard.account_bank)
                except Exception as exception_obj:
                    msg = exception_obj.args
                    raise osv.except_osv(_('ERROR!'),msg)
                if not account_info:
                    raise osv.except_osv(
                        _('ERROR!'),
                        _('Statements found for unknown account %(bank_account)s') %
                        {'bank_account': statement.local_account})
                #Check for journal in account_info
                if 'journal_id' not in account_info.keys():
                    raise osv.except_osv(
                        _('ERROR!'),
                        _('Statements found for account %(bank_account)s, '
                          'but no default journal was defined.') %
                        {'bank_account': statement.local_account})
                # Get required currency code overwriting fallback
                currency_code = account_info.currency_id.name
                # Cache results
                if not statement.local_account in info:
                    info[statement.local_account] = {
                        currency_code: account_info
                    }
                else:
                    info[statement.local_account][currency_code] = account_info
            # Account_info obtained and cached
            # Final check: no coercion of currencies!
            if statement.local_currency \
               and account_info.currency_id.name != statement.local_currency:
                # TODO: convert currencies?
                raise osv.except_osv(
                    _('ERROR!'),
                    _('Statement %(statement_id)s for account %(bank_account)s'
                      ' uses different currency than the defined bank journal.') %
                    {
                     'bank_account': statement.local_account,
                     'statement_id': statement.id
                     })
            # Check existence of previous statement
            # Less well defined formats can resort to a 
            # dynamically generated statement identification
            # (e.g. a datetime string of the moment of import)
            # and have potential duplicates flagged by the 
            # matching procedure
            statement_ids = statement_obj.search(cr, uid,
                            [('name', '=', statement.id),
                             ('date', '=', date2str(statement.date)),])
            if statement_ids:
                raise osv.except_osv(
                    _('ERROR!'),
                    _('Statement %(id)s known - skipped') %
                    {'id': statement.id})
            # Get the period for the statement (as bank statement object checks this)
            period_ids = period_obj.search(cr, uid,
                                           [('company_id','=',company.id),
                                            ('date_start','<=',statement.date),
                                            ('date_stop','>=',statement.date),
                                            ('special', '=', False)])
            if not period_ids:
                raise osv.except_osv(
                    _('ERROR!'),
                    _('No period found covering statement date %s, '
                      'statement %s') % (statement.date.strftime('%Y-%m-%d'), statement.id))
            # Create the bank statement record
            statement_id = statement_obj.create(cr, uid, dict(
                name = statement.id,
                journal_id = account_info.journal_id.id,
                date = date2str(statement.date),
                balance_start = statement.start_balance,
                balance_end_real = statement.end_balance,
                balance_end = statement.end_balance,
                state = 'draft',
                user_id = uid,
                banking_id = import_id,
                company_id = company.id,
                period_id = period_ids[0],))
            imported_statement_ids.append(statement_id)
            # Process Transactions
            subno = 0
            for transaction in statement.transactions:
                subno += 1
                #Assign Transaction number if not available
                if not transaction.id:
                    transaction.id = str(subno)
                values = {}
                for attr in transaction.__slots__ + ['type']:
                    if attr in import_transaction_obj.column_map:
                        values[import_transaction_obj.column_map[attr]] = eval('transaction.%s' % attr)
                    elif attr in import_transaction_obj._columns:
                        values[attr] = eval('transaction.%s' % attr)
                values['statement_id'] = statement_id
                values['bank_country_code'] = bank_country_code
                values['local_account'] = statement.local_account
                values['local_currency'] = statement.local_currency
                transaction_id = import_transaction_obj.create(cr, uid, values, context=context)
                if transaction_id:
                    transaction_ids.append(transaction_id)
                else:
                    raise osv.except_osv(
                         _('ERROR!'),
                         _('Failed to create an import transaction resource'))
                    
        import_transaction_obj.match(cr, uid, transaction_ids, bank_import_wizard.account_bank, context=context)
            
        #recompute statement end_balance for validation
        statement_obj.button_dummy(cr, uid, imported_statement_ids, context=context)
        
        # Update Imported File
        state = 'ready'
        statement_file_obj.write(cr, uid, import_id, dict(state = state), context)
        if not imported_statement_ids:# or not results.trans_loaded_cnt:
            # file state can be 'ready' while import state is 'error'
            state = 'error'
        self.write(cr, uid, [ids[0]], dict(
                                           import_id = import_id,
                                           state = state,
                                           statement_ids = [(6, 0, imported_statement_ids)],
                                           ), context)
        return {
            'name': (state == 'ready' and _('Review Bank Statements') or
                     _('Error')),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(context, active_ids=ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0] or False,
        }

    _columns = {
                'company': fields.many2one('res.company', 'Company', required=True,
                                           states = {
                                                     'ready': [('readonly', True)],
                                                     'error': [('readonly', True)],
                                                     }),
                'file': fields.binary('Statements File',
                                      states = {
                                                'ready': [('readonly', True)],
                                                'error': [('readonly', True)],
                                                }),
                'parser': fields.selection(parser_types, 'File Format',
                                           states = {
                                                     'ready': [('readonly', True)],
                                                     'error': [('readonly', True)],
                                                     }),
                'state': fields.selection([('init', 'init'),
                                           ('ready', 'ready'),
                                           ('error', 'error')],
                                          'State', readonly=True),
                'import_id': fields.many2one('account.banking.ccorp.imported.file', 'Import File'),
                'statement_ids': fields.many2many('account.bank.statement', 'rel_wiz_statements',
                                                  'wizard_id','statement_id', 'Imported Bank Statements'),
                'line_ids': fields.one2many('account.banking.ccorp.bank.import.line', 'banking_import_id',
                                            'Transactions'),
                'account_bank': fields.many2one('res.partner.bank', 'Account',
                                                states = {
                                                          'ready': [('readonly', True)],
                                                          'error': [('readonly', True)],
                                                          }),
                'date_from':fields.date('Date from', states = {
                                                               'ready': [('readonly', True)],
                                                               'error': [('readonly', True)]
                                                               }),
                'date_to':fields.date('Date to', states = {
                                                           'ready': [('readonly', True)],
                                                           'error': [('readonly', True)]
                                                           }),
                'ending_balance': fields.float('Ending balance', digits=(16, 2),
                                               states = {
                                                         'ready': [('readonly', True)],
                                                         'error': [('readonly', True)],
                                                         }),
                }
    
    #Used on view onchange event
    def onchange_account_parser(self, cr, uid, ids, account_bank=False, context=None):
        if account_bank:
            account_parser = self.pool.get('res.partner.bank').browse(cr, uid, account_bank, context=context).parser_types
            if account_parser:
                return {'value':{'parser': account_parser}}
        return {'value':{'parser': False}}
    
    def extract_number( self, account_number ):
        '''
        Extracts symbols from account_number using
        regular expression r'[0-9]+'
        '''
        cad = ''
        result = re.findall(r'[0-9]+', account_number)
               
        for character in result:
            cad = cad + character
        return cad

    _defaults = {
        'state': 'init',
        'ending_balance': 0.0,
        'company': lambda s,cr,uid,c:
            s.pool.get('res.company')._company_default_get(cr, uid, 'bank.import.transaction', context=c),
        }