# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from openerp.report import report_sxw
from openerp import models, _
from openerp.exceptions import Warning

CURRENCY_NAMES = {
    'USD': {
        'en': 'Dollars',
        'es': 'DOLARES',
    },
    'EUR': {
        'en': 'Euros',
        'es': 'EUROS',
    },
    'CRC': {
        'en': 'Colones',
        'es': 'COLONES',
    }
}


class ReportAccountPayment(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportAccountPayment, self).__init__(cr, uid, name,
                                                   context=context)
        self.localcontext.update({
            'get_text_amount': self._get_text_amount,
        })

    def _get_currency_name(self, currency_id):
        currency_obj = self.pool.get('res.currency')
        currency = currency_obj.browse(self.cr, self.uid, currency_id)
        lang = self.localcontext.get('lang')
        if currency.name in CURRENCY_NAMES:
            return CURRENCY_NAMES[currency.name][lang]
        raise Warning(_('Currency not supported by this report.'))

    def _get_text_amount(self, amount, currency_id):
        es_regex = re.compile('es.*')
        en_regex = re.compile('en.*')
        lang = self.localcontext.get('lang')
        if es_regex.match(lang):
            from openerp.addons.l10n_cr_amount_to_text import amount_to_text
            return amount_to_text.number_to_text_es(
                amount, '',
                join_dec=' Y ', separator=',', decimal_point='.')
        elif en_regex.match(lang):
            from openerp.tools import amount_to_text_en
            return amount_to_text_en.amount_to_text(
                amount, lang='en', currency='')
        else:
            raise Warning(_('Language not supported by this report.'))


class report_account_payment(models.AbstractModel):
    _name = 'report.account_payment_report.account_payment_report'
    _inherit = 'report.abstract_report'
    _template = 'account_payment_report.account_payment_report'
    _wrapped_report_class = ReportAccountPayment
