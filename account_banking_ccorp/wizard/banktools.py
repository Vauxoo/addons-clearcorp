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

import datetime
from tools.translate import _
from account_banking_ccorp.parsers import convert
from account_banking_ccorp import sepa
from account_banking_ccorp.struct import struct

__all__ = [
    'get_period',
    'get_bank_accounts',
    'get_partner',
    'get_country_id',
    'get_company_bank_account',
    'create_bank_account',
]

def get_period(pool, cursor, uid, date, company):
    '''
    Get a suitable period for the given date range and the given company.
    '''
    fiscalyear_obj = pool.get('account.fiscalyear')
    period_obj = pool.get('account.period')
    # If not data available using today
    if not date:
        date = convert.date2str(datetime.datetime.today())
    search_date = convert.date2str(date)
    fiscalyear_ids = fiscalyear_obj.search(cursor, uid,
                    [('date_start','<=', search_date),
                     ('date_stop','>=', search_date),
                     ('state','=','draft'),
                     ('company_id','=',company.id)])
    if not fiscalyear_ids:
        fiscalyear_ids = fiscalyear_obj.search(cursor, uid,
                        [('date_start','<=',search_date),
                         ('date_stop','>=',search_date),
                         ('state','=','draft'),
                         ('company_id','=',None)])
    if not fiscalyear_ids:
        raise Exception(
            _('No suitable fiscal year found for date %(date)s and company %(company_name)s') %
            dict(company_name=company.name, date=date))
    elif len(fiscalyear_ids) > 1:
        raise Exception(
            _('Multiple overlapping fiscal years found for date %(date)s and company %(company_name)s') %
            dict(company_name=company.name, date=date))
    fiscalyear_id = fiscalyear_ids[0]
    period_ids = period_obj.search(cursor, uid,
                            [('date_start','<=',search_date),
                             ('date_stop','>=',search_date),
                             ('fiscalyear_id','=',fiscalyear_id),
                             ('state','=','draft'),
                             ('special', '=', False),])
    if not period_ids:
        raise Exception(
            _('No suitable period found for date %(date)s and company %(company_name)s') %
            dict(company_name=company.name, date=date))
    if len(period_ids) != 1:
        raise Exception(
            _('Multiple overlapping periods for date %(date)s and company %(company_name)s') %
            dict(company_name=company.name, date=date))
    return period_ids[0]

def get_bank_accounts(pool, cr, uid, account_number, fail=False):
    '''
    Get the bank account related to the given account number
    '''
    # No need to search for nothing
    if not account_number:
        return []
    partner_bank_obj = pool.get('res.partner.bank')
    bank_account_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=', account_number)])
    if not bank_account_ids:
        if not fail:
            raise Exception(
                _('Bank account %(account_no)s was not found in the database') %
                dict(account_no=account_number),)
        return []
    return partner_bank_obj.browse(cr, uid, bank_account_ids)

def _has_attr(obj, attr):
    # Needed for dangling addresses and a weird exception scheme in
    # OpenERP's orm.
    try:
        return bool(getattr(obj, attr))
    except KeyError:
        return False
    
def get_partner(pool, cr, uid, name, address, postal_code, city,
                country_id, context=None):
    '''
    Get the partner belonging to the account holders name <name>

    If multiple partners are found with the same name, select the first and
    add a warning to the import log.
 
    TODO: revive the search by lines from the address argument
    '''
    partner_obj = pool.get('res.partner')
    partner_ids = partner_obj.search(cr, uid, [('name', 'ilike', name)],
                                     context=context)
    if not partner_ids:
        # Try brute search on address and then match reverse
        criteria = []
        if country_id:
            criteria.append(('address.country_id', '=', country_id))
        if city:
            criteria.append(('address.city', 'ilike', city))
        if postal_code:
            criteria.append(('address.zip', 'ilike', postal_code))
        partner_search_ids = partner_obj.search(cr, uid, criteria, context=context)
        if (not partner_search_ids and country_id):
            # Try again with country_id = False
            criteria[0] = ('address.country_id', '=', False)
            partner_search_ids = partner_obj.search(cr, uid, criteria, context=context)
        key = name.lower()
        partners = []
        for partner in partner_obj.read(
            cr, uid, partner_search_ids, ['name'], context=context):
            if (len(partner['name']) > 3 and partner['name'].lower() in key):
                partners.append(partner)
        partners.sort(key=lambda x: len(x['name']), reverse=True)
        partner_ids = [x['id'] for x in partners]
    return partner_ids and partner_ids[0] or False

def get_company_bank_account(pool, cr, uid, account_number, currency, company, bank_accounts):
    '''
    Get the matching bank account for this company. Currency is the ISO code
    for the requested currency.
    '''
    results = struct()
    if not bank_accounts:
        return False
    if bank_accounts.partner_id.id != company.partner_id.id:
        raise Exception(
            _('Account %(account_no)s is not owned by %(partner)s') %
            dict(account_no = account_number, partner = company.partner_id.name))
    results.account = bank_accounts
    bank_settings_obj = pool.get('res.partner.bank')
    bank_accounts = bank_accounts
    results.company_id = company
    results.journal_id = bank_accounts.journal_id
     # Take currency from bank_account or from company
    if bank_accounts.journal_id.currency.id:
        results.currency_id = bank_accounts.journal_id.currency
    else:
        results.currency_id = company.currency_id
    # Rest just copy/paste from settings
    results.default_debit_account_id = bank_accounts.default_debit_account_id
    results.default_credit_account_id = bank_accounts.default_credit_account_id
    #results.costs_account_id = settings.costs_account_id
    #results.invoice_journal_id = settings.invoice_journal_id
    results.bank_partner_id = bank_accounts.id
    return results

def get_or_create_bank(pool, cursor, uid, bic, online=False, code=None, name=None):
    '''
    Find or create the bank with the provided BIC code.
    When online, the SWIFT database will be consulted in order to
    provide for missing information.
    '''
    # UPDATE: Free SWIFT databases are since 2/22/2010 hidden behind an
    #         image challenge/response interface.

    bank_obj = pool.get('res.bank')

    # Self generated key?
    if len(bic) < 8:
        # search key
        bank_ids = bank_obj.search(
            cursor, uid, [
                ('bic', '=', bic[:6])
            ])
        if not bank_ids:
            bank_ids = bank_obj.search(
                cursor, uid, [
                    ('bic', 'ilike', bic + '%')
                ])
    else:
        bank_ids = bank_obj.search(
            cursor, uid, [
                ('bic', '=', bic)
            ])

    if bank_ids and len(bank_ids) == 1:
        banks = bank_obj.browse(cursor, uid, bank_ids)
        return banks[0].id, banks[0].country.id

    country_obj = pool.get('res.country')
    country_ids = country_obj.search(
        cursor, uid, [('code', '=', bic[4:6])]
    )
    country_id = country_ids and country_ids[0] or False
    bank_id = False

    if online:
        info, address = sepa.online.bank_info(bic)
        if info:
            bank_id = bank_obj.create(cursor, uid, dict(
                code = info.code,
                name = info.name,
                street = address.street,
                street2 = address.street2,
                zip = address.zip,
                city = address.city,
                country = country_id,
                bic = info.bic[:8],
            ))
    else:
        info = struct(name=name, code=code)

    if not online or not bank_id:
        bank_id = bank_obj.create(cursor, uid, dict(
            code = info.code or 'UNKNOW',
            name = info.name or _('Unknown Bank'),
            country = country_id,
            bic = bic,
        ))
    return bank_id, country_id

def get_country_id(pool, cr, uid, transaction, context=None):
    """
    Derive a country id from the info on the transaction.
    
    :param transaction: browse record of a transaction
    :returns: res.country id or False 
    """
    
    country_code = False
    iban = sepa.IBAN(transaction.remote_account)
    if iban.valid:
        country_code = iban.countrycode
    elif transaction.remote_owner_country_code:
        country_code = transaction.remote_owner_country_code
    # fallback on the import parsers country code
    elif transaction.bank_country_code:
        country_code = transaction.bank_country_code
    if country_code:
        country_ids = pool.get('res.country').search(
            cr, uid, [('code', '=', country_code.upper())],
            context=context)
        country_id = country_ids and country_ids[0] or False
    if not country_id:
        company = transaction.statement_line_id.company_id
        if company.partner_id.country:
            country_id = company.partner_id.country.id
    return country_id

def create_bank_account(pool, cr, uid, partner_id,account_number, holder_name,
                        address, city, country_id, bic=False, context=None):
    '''
    Create a matching bank account with this holder for this partner.
    '''
    values = struct(
        partner_id = partner_id,
        owner_name = holder_name,
        country_id = country_id,
    )
    bankcode = None

    # Are we dealing with IBAN?
    iban = sepa.IBAN(account_number)
    if iban.valid:
        # Take as much info as possible from IBAN
        values.state = 'iban'
        values.acc_number = str(iban)
        #values.acc_number_domestic = iban.BBAN
        bankcode = iban.bankcode + iban.countrycode
    else:
        # No, try to convert to IBAN
        values.state = 'bank'
        values.acc_number = account_number
        if country_id:
            country_code = pool.get('res.country').read(
                cr, uid, country_id, ['code'], context=context)['code']
            if country_code in sepa.IBAN.countries:
                account_info = sepa.online.account_info(
                    country_code, values.acc_number)
                if account_info:
                    values.acc_number = iban = account_info.iban
                    values.state = 'iban'
                    bankcode = account_info.code
                    bic = account_info.bic

    if bic:
        values.bank = get_or_create_bank(pool, cr, uid, bic)[0]
        values.bank_bic = bic

    # Create bank account and return
    return pool.get('res.partner.bank').create(
        cr, uid, values, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
